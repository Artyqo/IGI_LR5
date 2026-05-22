import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count, Q, F, DecimalField, ExpressionWrapper
from django.conf import settings

import pytz
import calendar
from django.utils import timezone as dj_timezone

from .models import (
    Country, News, CompanyInfo, Review, Tour,
    FAQ, Vacancy, PromoCode, Employee, Client, Order, Hotel
)
from .forms import ClientRegistrationForm, TourForm

from statistics import mean, median, mode, StatisticsError
import datetime

import io
import matplotlib
matplotlib.use('Agg')  # Обязательно — без GUI, для сервера
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from django.http import HttpResponse

import logging
logger = logging.getLogger('agency')


# =========================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ПРОВЕРКИ РОЛЕЙ
# Принцип: каждая функция либо возвращает True, либо бросает PermissionDenied
# =========================================================================

def is_superuser_only(user):
    """Только суперпользователь (владелец агентства)"""
    if user.is_authenticated and user.is_superuser:
        return True
    raise PermissionDenied


def get_user_role(user):
    """
    Возвращает строку-роль пользователя:
    - 'admin'      — суперпользователь
    - 'employee'   — сотрудник агентства
    - 'client'     — зарегистрированный клиент
    - 'guest'      — не вошедший в систему
    """
    if not user.is_authenticated:
        return 'guest'
    if user.is_superuser:
        return 'admin'
    if hasattr(user, 'employee_profile'):
        return 'employee'
    if hasattr(user, 'client_profile'):
        return 'client'
    # Аккаунт есть, но ни сотрудник, ни клиент — редкий edge-case
    return 'registered'


def get_role_label(role):
    return {
        'admin':      'Администратор',
        'employee':   'Сотрудник',
        'client':     'Клиент',
        'registered': 'Пользователь',
        'guest':      'Гость',
    }.get(role, 'Пользователь')


def as_int_or_none(value):
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None


# =========================================================================
# WEATHER API — OpenWeatherMap
# Добавьте в settings.py: OPENWEATHER_API_KEY = "ваш_ключ"
# Бесплатный ключ: https://openweathermap.org/api
# =========================================================================

# Маппинг: русское название страны → столица для точного запроса к API.
# Запрос по столице даёт корректную погоду (запрос по стране ненадёжен).
COUNTRY_CAPITAL_MAP = {
    'Испания':   'Madrid',
    'Египет':    'Cairo',
    'Италия':    'Rome',
    'Франция':   'Paris',
    'Турция':    'Ankara',
    'Греция':    'Athens',
    'Таиланд':   'Bangkok',
    'Мальдивы':  'Male',
    'ОАЭ':       'Abu Dhabi',
    'Германия':  'Berlin',
    'Кипр':      'Nicosia',
    'Португалия':'Lisbon',
    'Хорватия':  'Zagreb',
    'Куба':      'Havana',
    'Индия':     'New Delhi',
}

# Русские названия столиц — для отображения пользователю
CAPITAL_RU_MAP = {
    'Madrid':    'Мадрид',
    'Cairo':     'Каир',
    'Rome':      'Рим',
    'Paris':     'Париж',
    'Ankara':    'Анкара',
    'Athens':    'Афины',
    'Bangkok':   'Бангкок',
    'Male':      'Мале',
    'Abu Dhabi': 'Абу-Даби',
    'Berlin':    'Берлин',
    'Nicosia':   'Никосия',
    'Lisbon':    'Лиссабон',
    'Zagreb':    'Загреб',
    'Havana':    'Гавана',
    'New Delhi': 'Нью-Дели',
}


def get_weather_for_country(country_name):
    """
    Запрашивает текущую погоду через OpenWeatherMap API.
    Запрос делается по столице страны — это надёжнее чем по названию страны.
    Возвращает словарь с данными или None при ошибке / отсутствии ключа.
    """
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    if not api_key:
        return None

    capital_en = COUNTRY_CAPITAL_MAP.get(country_name)
    if not capital_en:
        return None  # Страна не в маппинге — лучше не показывать, чем показать неверное

    try:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'q':     capital_en,
            'appid': api_key,
            'units': 'metric',  # °C
            'lang':  'ru',      # описание погоды на русском
        }
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city_en = data.get('name', capital_en)
            city_ru = CAPITAL_RU_MAP.get(city_en, city_en)
            return {
                'temp':        round(data['main']['temp']),
                'feels_like':  round(data['main']['feels_like']),
                'humidity':    data['main']['humidity'],
                'description': data['weather'][0]['description'].capitalize(),
                'icon':        data['weather'][0]['icon'],
                'wind_speed':  data['wind']['speed'],
                'city_ru':     city_ru,   # "Каир" — для отображения
            }
    except requests.RequestException as e:
        logger.error(f'Ошибка запроса погоды для {country_name}: {e}')

    return None

def get_nbrb_rates():
    """
    Получает курсы валют с API Национального банка РБ.
    Возвращает словарь с курсами EUR и USD к BYN или None при ошибке.
    API: https://api.nbrb.by/exrates/rates?periodicity=0
    Без ключа, бесплатно, официальный источник.
    """
    try:
        url = 'https://api.nbrb.by/exrates/rates?periodicity=0'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            rates_list = resp.json()
            result = {}
            for rate in rates_list:
                if rate.get('Cur_Abbreviation') == 'USD':
                    result['USD'] = round(rate['Cur_OfficialRate'] / rate['Cur_Scale'], 4)
                elif rate.get('Cur_Abbreviation') == 'EUR':
                    result['EUR'] = round(rate['Cur_OfficialRate'] / rate['Cur_Scale'], 4)
                elif rate.get('Cur_Abbreviation') == 'RUB':
                    result['RUB'] = round(rate['Cur_OfficialRate'] / rate['Cur_Scale'], 4)
            return result if result else None
    except requests.RequestException as e:
        logger.error(f'Ошибка запроса курсов НБРБ: {e}')
    return None


# =========================================================================
# БЛОК 1: ОБЩИЕ СТРАНИЦЫ (ДОСТУПНЫ ВСЕМ — ГОСТЯМ И ЗАРЕГИСТРИРОВАННЫМ)
# =========================================================================

def index(request):
    latest_news = News.objects.order_by('-published_date').first()
    context = {'latest_news': latest_news}
    return render(request, 'agency/index.html', context)


def about(request):
    company_info = CompanyInfo.objects.first()
    return render(request, 'agency/about.html', {'company_info': company_info})


def news_list(request):
    news = News.objects.all()
    return render(request, 'agency/news_list.html', {'news': news})


def faq_list(request):
    faqs = FAQ.objects.all()
    return render(request, 'agency/faq.html', {'faqs': faqs})


def vacancy_list(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'agency/vacancies.html', {'vacancies': vacancies})


def promocode_list(request):
    active_promos  = PromoCode.objects.filter(is_active=True)
    archive_promos = PromoCode.objects.filter(is_active=False)
    return render(request, 'agency/promocodes.html', {
        'active_promos':  active_promos,
        'archive_promos': archive_promos,
    })


def contacts_view(request):
    employees = Employee.objects.all()
    return render(request, 'agency/contacts.html', {'employees': employees})


def privacy_policy(request):
    return render(request, 'agency/privacy.html')


def reviews(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            logger.debug('Незарегистрированный пользователь попытался оставить отзыв')
            messages.error(request, "Чтобы оставить отзыв, войдите в аккаунт.")
            return redirect('login')
        if not hasattr(request.user, 'client_profile'):
            logger.warning(f'Пользователь без роли клиента попытался оставить отзыв: {request.user.username}')
            messages.error(request, "Отзывы могут оставлять только зарегистрированные клиенты.")
            return redirect('reviews')

        author = request.POST.get('author_name') or request.user.username
        text   = request.POST.get('text')
        rating = request.POST.get('rating')
        if author and text and rating:
            Review.objects.create(
                user=request.user,
                author_name=author,
                text=text,
                rating=int(rating),
            )
            logger.info(f'Клиент {request.user.username} оставил отзыв с оценкой {rating}')
            messages.success(request, "Спасибо, отзыв сохранён.")
        return redirect('reviews')

    all_reviews = Review.objects.order_by('-date_created')
    return render(request, 'agency/reviews.html', {
        'all_reviews': all_reviews,
        'can_review':  get_user_role(request.user) == 'client',
    })


# =========================================================================
# БЛОК 2: КАТАЛОГ ТУРОВ — READ (доступен всем)
# =========================================================================

def tour_list(request):
    total_price = ExpressionWrapper(
        F('hotel__price_per_day') * F('duration_weeks') * 7,
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    tours     = Tour.objects.select_related('hotel', 'hotel__country').annotate(
        total_price_calc=total_price
    )
    countries = Country.objects.all()

    # --- Фильтрация ---
    country_id = request.GET.get('country')
    max_price  = request.GET.get('price')
    stars      = request.GET.get('stars')
    is_hot     = request.GET.get('is_hot')
    search     = request.GET.get('q', '').strip()
    sort       = request.GET.get('sort', 'departure')

    selected_country = as_int_or_none(country_id)
    selected_stars   = as_int_or_none(stars)

    if selected_country:
        tours = tours.filter(hotel__country_id=selected_country)
    if max_price:
        tours = tours.filter(total_price_calc__lte=max_price)
    if selected_stars:
        tours = tours.filter(hotel__stars=selected_stars)
    if is_hot == '1':
        tours = tours.filter(is_hot=True)
    if search:
        tours = tours.filter(
            Q(title__icontains=search) |
            Q(hotel__name__icontains=search) |
            Q(hotel__country__name__icontains=search)
        )

    # --- Сортировка ---
    sort_fields = {
        'departure':  'departure_date',
        'price_asc':  'total_price_calc',
        'price_desc': '-total_price_calc',
        'country':    'hotel__country__name',
        'stars_desc': '-hotel__stars',
    }
    tours = tours.order_by(sort_fields.get(sort, 'departure_date'))

    role = get_user_role(request.user)

    context = {
        'tours':            tours,
        'countries':        countries,
        'selected_country': selected_country,
        'selected_price':   max_price,
        'selected_stars':   selected_stars,
        'selected_hot':     is_hot,
        'search_query':     search,
        'selected_sort':    sort,
        # Флаги для шаблона
        'can_manage':       role == 'admin',   # создание тура видит только admin
        'role':             role,
    }
    return render(request, 'agency/tour_list.html', context)


def tour_detail(request, pk):
    tour = get_object_or_404(
        Tour.objects.select_related('hotel', 'hotel__country'), pk=pk
    )
    role    = get_user_role(request.user)
    weather = get_weather_for_country(tour.hotel.country.name)
    rates   = get_nbrb_rates()

    # Конвертация цены тура в другие валюты
    currency_prices = None
    if rates and tour.price:
        price = float(tour.price)
        currency_prices = {
            'USD': round(price / rates['USD'], 2) if 'USD' in rates else None,
            'EUR': round(price / rates['EUR'], 2) if 'EUR' in rates else None,
            'RUB': round(price / rates['RUB'], 2) if 'RUB' in rates else None,
            'usd_rate': rates.get('USD'),
            'eur_rate': rates.get('EUR'),
            'rub_rate': rates.get('RUB'),
        }

    employees = Employee.objects.all() if role == 'client' else None

    return render(request, 'agency/tour_detail.html', {
        'tour':            tour,
        'role':            role,
        'can_buy':         role == 'client',
        'can_manage':      role == 'admin',
        'weather':         weather,
        'employees':       employees,
        'currency_prices': currency_prices,
    })


# =========================================================================
# БЛОК 3: CRUD ТУРОВ — CREATE / UPDATE / DELETE (только superuser)
#
# Матрица доступа:
#   Гость         → только READ (список + детали)
#   Клиент        → READ + покупка (tour_buy)
#   Сотрудник     → READ (видит всё, но не управляет каталогом)
#   Admin (super) → READ + CREATE + UPDATE + DELETE
# =========================================================================

@user_passes_test(is_superuser_only)
def tour_create(request):
    """CREATE: добавление новой путёвки в каталог — только для admin."""
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f'Администратор {request.user.username} создал тур: {tour.title}')
            messages.success(request, "Путёвка успешно добавлена в каталог!")
            return redirect('tour_list')
    else:
        logger.warning(f'Ошибка создания тура: {form.errors}')
        form = TourForm()
    return render(request, 'agency/tour_form.html', {
        'form':   form,
        'action': 'Добавить новую',
    })


@user_passes_test(is_superuser_only)
def tour_update(request, pk):
    """UPDATE: редактирование путёвки — только для admin."""
    tour = get_object_or_404(Tour, pk=pk)
    if request.method == 'POST':
        form = TourForm(request.POST, instance=tour)
        if form.is_valid():
            form.save()
            logger.info(f'Администратор {request.user.username} обновил тур: {tour.title}')
            messages.success(request, "Изменения сохранены.")
            return redirect('tour_detail', pk=tour.pk)
    else:
        logger.warning(f'Ошибка обновления тура {pk}: {form.errors}')
        form = TourForm(instance=tour)
    return render(request, 'agency/tour_form.html', {
        'form':   form,
        'action': 'Сохранить изменения',
    })


@user_passes_test(is_superuser_only)
def tour_delete(request, pk):
    """DELETE: удаление путёвки — только для admin."""
    tour = get_object_or_404(Tour, pk=pk)
    if request.method == 'POST':
        logger.warning(f'Администратор {request.user.username} удалил тур: {tour.title}')
        tour.delete()
        messages.success(request, "Путёвка удалена.")
        return redirect('tour_list')
    return render(request, 'agency/tour_confirm_delete.html', {'tour': tour})


# =========================================================================
# БЛОК 4: ПОКУПКА ТУРА — только для клиента (role == 'client')
# ИСПРАВЛЕНИЕ: убран дублирующий @login_required, логика проверки роли
# перенесена внутрь view — это даёт понятное сообщение вместо 403
# =========================================================================

@login_required
def tour_buy(request, pk):
    """
    Оформление покупки путёвки.
    Доступно ТОЛЬКО пользователям с ролью 'client'.
    Гость → редирект на логин.
    Сотрудник / admin → сообщение об ошибке.
    """
    role = get_user_role(request.user)

    # Проверяем роль внутри view (без @user_passes_test, чтобы показать нормальное сообщение)
    if role != 'client':
        logger.warning(f'Попытка покупки тура пользователем без роли клиента: {request.user.username}')
        messages.error(
            request,
            "Оформлять покупки могут только зарегистрированные клиенты. "
            "Если вы хотите купить путёвку, зарегистрируйтесь как клиент."
        )
        return redirect('tour_detail', pk=pk)

    tour           = get_object_or_404(Tour, pk=pk)
    client_profile = request.user.client_profile

    # Клиент выбирает менеджера в форме (поле employee_id).
    # Если не выбрал (или выбор некорректный) — проверяем прошлые заказы,
    # и только если заказов нет — берём первого доступного сотрудника.
    employee_id = request.POST.get('employee_id')
    assigned_employee = None

    if employee_id:
        assigned_employee = Employee.objects.filter(pk=employee_id).first()

    if not assigned_employee:
        last_order = Order.objects.filter(client=client_profile).select_related('employee').first()
        assigned_employee = last_order.employee if last_order else Employee.objects.first()

    if not assigned_employee:
        messages.error(
            request,
            "Извините, в агентстве пока нет сотрудников для оформления заказа."
        )
        return redirect('tour_detail', pk=pk)

    order = Order.objects.create(
        client=client_profile,
        employee=assigned_employee,
        total_cost=tour.price,
    )
    order.tours.add(tour)
    logger.info(f'Клиент {request.user.username} купил тур: {tour.title} (заказ №{order.id})')

    messages.success(
        request,
        f"Тур «{tour.title}» успешно оформлен! "
        f"Ваш менеджер: {assigned_employee.full_name}."
    )
    return redirect('profile')


# =========================================================================
# БЛОК 5: ЛИЧНЫЙ КАБИНЕТ — разное содержимое по роли
# =========================================================================

@login_required
def profile_view(request):
    user = request.user
    role = get_user_role(user)
    context = {
        'role':       role,
        'role_label': get_role_label(role),
    }

    if role == 'admin':
        context['hotels']  = Hotel.objects.select_related('country').all()
        context['clients'] = Client.objects.prefetch_related('orders__tours').annotate(
            total_tours_count=Count('orders__tours'),
            total_spent=Sum('orders__total_cost'),
        )

    elif role == 'employee':
        context['employee']   = user.employee_profile
        context['orders']     = (
            Order.objects
            .filter(employee=user.employee_profile)
            .select_related('client')
            .prefetch_related('tours')
            .order_by('-created_at')
        )
        context['my_clients'] = (
            Client.objects
            .filter(orders__employee=user.employee_profile)
            .distinct()
            .order_by('last_name')
        )

    elif role == 'client':
        context['client']     = user.client_profile
        context['orders']     = (
            Order.objects
            .filter(client=user.client_profile)
            .select_related('employee')
            .prefetch_related('tours')
            .order_by('-created_at')
        )
        context['promocodes'] = PromoCode.objects.filter(is_active=True)

    else:
        # Аккаунт есть, но роль не назначена
        messages.warning(
            request,
            "Ваша учётная запись не привязана ни к одной роли. "
            "Обратитесь к администратору."
        )
        return redirect('index')

    # =========================================================================
    # БЛОК ВРЕМЕНИ: тайм-зона, текущая дата, календарь
    # =========================================================================
    utc_now = dj_timezone.now()  # datetime в UTC (timezone.now() возвращает UTC)

    # Определяем тайм-зону пользователя из профиля
    user_tz_name = 'Europe/Minsk'  # fallback
    if role == 'client' and hasattr(user, 'client_profile'):
        user_tz_name = user.client_profile.timezone
    elif role == 'employee' and hasattr(user, 'employee_profile'):
        user_tz_name = user.employee_profile.timezone
    elif role == 'admin':
        user_tz_name = 'Europe/Minsk'

    user_tz = pytz.timezone(user_tz_name)

    def convert_dt(dt):
        """Конвертирует datetime из UTC в тайм-зону пользователя."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(user_tz)

    if role == 'client':
        orders = list(context['orders'])
        for order in orders:
            order.created_at_local = convert_dt(order.created_at)
            order.created_at_utc = order.created_at.astimezone(pytz.utc)
            # Форматируем как строки
            order.created_at_local_str = order.created_at_local.strftime('%d/%m/%Y %H:%M')
            order.created_at_utc_str = order.created_at_utc.strftime('%d/%m/%Y %H:%M')
        context['orders'] = orders

    elif role == 'employee':
        orders = list(context['orders'])
        for order in orders:
            order.created_at_local = convert_dt(order.created_at)
            order.created_at_utc = order.created_at.astimezone(pytz.utc)
            # Добавляем отформатированные строки (как для клиента)
            order.local_time_str = order.created_at_local.strftime('%d/%m/%Y %H:%M')
            order.utc_time_str = order.created_at_utc.strftime('%d/%m/%Y %H:%M')
        context['orders'] = orders

    local_now = utc_now.astimezone(user_tz)
    utc_explicit = utc_now.astimezone(pytz.utc)

    # Текстовый календарь на текущий месяц
    cal_text = calendar.month(local_now.year, local_now.month)

    context.update({
        'utc_now_str':   utc_explicit.strftime('%d/%m/%Y %H:%M'),
        'local_now_str': local_now.strftime('%d/%m/%Y %H:%M'),
        'user_tz_name':  user_tz_name,
        'cal_text':      cal_text,
    })

    return render(request, 'agency/profile.html', context)


# =========================================================================
# БЛОК 6: АУТЕНТИФИКАЦИЯ
# =========================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                logger.info(f'Пользователь {user.username} вошёл в систему')
                # Редирект на страницу, с которой пришли (если была)
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
        else:
            logger.warning(f'Неудачная попытка входа: {request.POST.get("username")}')
            messages.error(request, "Неверный логин или пароль.")
    else:
        form = AuthenticationForm()

    return render(request, 'agency/login.html', {'form': form})


def logout_view(request):
    logger.info(f'Пользователь {request.user.username} вышел из системы')
    logout(request)
    return redirect('index')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'Новый клиент зарегистрирован: {user.username}')
            messages.success(request, "Добро пожаловать! Аккаунт успешно создан.")
            return redirect('profile')
    else:
        logger.warning(f'Неудачная регистрация: {request.POST.get("username")}')
        form = ClientRegistrationForm()

    return render(request, 'agency/register.html', {'form': form})

# =========================================================================
# БЛОК 7: СТАТИСТИКА — только для администратора
# =========================================================================

@user_passes_test(is_superuser_only)
def statistics_view(request):
    # ── 1. Клиенты в алфавитном порядке с общей суммой продаж ──────────────
    clients_alpha = (
        Client.objects
        .annotate(total_spent=Sum('orders__total_cost'))
        .order_by('last_name', 'first_name')
    )

    # ── 2. Статистические показатели по сумме продаж ───────────────────────
    sales_values = [
        float(c.total_spent)
        for c in clients_alpha
        if c.total_spent is not None
    ]

    sales_stats = {}
    if sales_values:
        try:
            sales_stats = {
                'mean':   round(mean(sales_values), 2),
                'median': round(median(sales_values), 2),
                'mode':   round(mode(sales_values), 2),
                'total':  round(sum(sales_values), 2),
                'count':  len(sales_values),
            }
        except StatisticsError:
            sales_stats = {
                'mean':   round(mean(sales_values), 2),
                'median': round(median(sales_values), 2),
                'mode':   None,   # mode бросает ошибку если нет единственной моды
                'total':  round(sum(sales_values), 2),
                'count':  len(sales_values),
            }

    # ── 3. Статистика по возрасту клиентов ─────────────────────────────────
    today = datetime.date.today()

    def calc_age(birth_date):
        if not birth_date:
            return None
        return (today.year - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day)))

    ages = [
        calc_age(c.birth_date)
        for c in Client.objects.all()
        if c.birth_date is not None
    ]
    ages = [a for a in ages if a is not None]

    age_stats = {}
    if ages:
        age_stats = {
            'mean':   round(mean(ages), 1),
            'median': round(median(ages), 1),
            'min':    min(ages),
            'max':    max(ages),
            'count':  len(ages),
        }

    # ── 4. Самое популярное направление (по количеству заказов) ────────────
    popular_countries = (
        Country.objects
        .annotate(tours_sold=Count('hotels__tours__orders'))
        .order_by('-tours_sold')
    )
    most_popular = popular_countries.first()

    # ── 5. Самое прибыльное направление (по сумме заказов) ─────────────────
    profitable_countries = (
        Country.objects
        .annotate(revenue=Sum('hotels__tours__orders__total_cost'))
        .order_by('-revenue')
    )
    most_profitable = profitable_countries.first()

    # ── 6. Статистика по звёздности отелей (для диаграммы позже) ───────────
    stars_stats = (
        Hotel.objects
        .values('stars')
        .annotate(count=Count('id'))
        .order_by('stars')
    )

    context = {
        'clients_alpha':       clients_alpha,
        'sales_stats':         sales_stats,
        'age_stats':           age_stats,
        'popular_countries':   popular_countries,
        'most_popular':        most_popular,
        'profitable_countries': profitable_countries,
        'most_profitable':     most_profitable,
        'stars_stats':         stars_stats,
    }
    return render(request, 'agency/statistics.html', context)

# =========================================================================
# ГРАФИКИ — генерация PNG на сервере через matplotlib (без JS)
# =========================================================================

def _check_admin(user):
    """Вспомогательная проверка для view-графиков."""
    return user.is_authenticated and user.is_superuser


def chart_sales_by_country(request):
    """
    График 1: Выручка по странам (горизонтальная столбчатая диаграмма).
    Отображает распределение продаж по группам (странам).
    """
    if not _check_admin(request.user):
        raise PermissionDenied

    data = (
        Country.objects
        .annotate(revenue=Sum('hotels__tours__orders__total_cost'))
        .filter(revenue__isnull=False)
        .order_by('revenue')
    )

    names    = [c.name for c in data]
    revenues = [float(c.revenue) for c in data]

    fig, ax = plt.subplots(figsize=(8, max(3, len(names) * 0.7)))
    bars = ax.barh(names, revenues, color='#4a90d9', edgecolor='#2c5f8a')

    # Подписи значений на столбцах
    for bar, val in zip(bars, revenues):
        ax.text(
            bar.get_width() + max(revenues) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{val:,.0f} BYN',
            va='center', ha='left', fontsize=9, color='#333'
        )

    ax.set_xlabel('Выручка (BYN)', fontsize=10)
    ax.set_title('Выручка по странам назначения', fontsize=13, fontweight='bold', pad=15)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax.set_xlim(0, max(revenues) * 1.2 if revenues else 1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    return _fig_to_response(fig)


def chart_tours_by_stars(request):
    """
    График 2: Распределение туров по звёздности отелей (круговая диаграмма).
    Показывает какой класс отелей наиболее популярен.
    """
    if not _check_admin(request.user):
        raise PermissionDenied

    data = (
        Hotel.objects
        .values('stars')
        .annotate(count=Count('tours__orders'))
        .filter(count__gt=0)
        .order_by('stars')
    )

    labels = [f"{'★' * d['stars']} ({d['stars']} зв.)" for d in data]
    sizes  = [d['count'] for d in data]
    colors = ['#d4e6f1', '#85c1e9', '#3498db', '#1a6fa8', '#0d3b6e'][:len(labels)]
    explode = [0.04] * len(labels)

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        explode=explode,
        startangle=140,
        textprops={'fontsize': 10},
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color('white')
        at.set_fontweight('bold')

    ax.set_title('Популярность классов отелей\n(по числу проданных туров)', fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()

    return _fig_to_response(fig)


def chart_orders_by_month(request):
    """
    График 3: Количество заказов по месяцам (линейный график).
    Показывает изменение показателей по датам.
    """
    if not _check_admin(request.user):
        raise PermissionDenied

    from django.db.models.functions import TruncMonth

    data = (
        Order.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'), revenue=Sum('total_cost'))
        .order_by('month')
    )

    if not data:
        # Пустой график с пояснением
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'Недостаточно данных', ha='center', va='center',
                fontsize=14, color='#999', transform=ax.transAxes)
        ax.set_title('Заказы по месяцам', fontsize=13, fontweight='bold')
        return _fig_to_response(fig)

    months   = [d['month'].strftime('%m/%Y') for d in data]
    counts   = [d['count'] for d in data]
    revenues = [float(d['revenue']) for d in data]

    fig, ax1 = plt.subplots(figsize=(9, 4))

    # Левая ось — количество заказов (столбцы)
    ax1.bar(months, counts, color='#a8d8ea', edgecolor='#5ba4cf',
            label='Кол-во заказов', zorder=2)
    ax1.set_ylabel('Количество заказов', fontsize=10, color='#3a7abf')
    ax1.tick_params(axis='y', labelcolor='#3a7abf')
    ax1.set_ylim(0, max(counts) * 1.4 if counts else 1)

    # Правая ось — выручка (линия)
    ax2 = ax1.twinx()
    ax2.plot(months, revenues, color='#e74c3c', marker='o',
             linewidth=2, markersize=6, label='Выручка (BYN)', zorder=3)
    ax2.set_ylabel('Выручка (BYN)', fontsize=10, color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    ax2.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, _: f'{x:,.0f}')
    )

    ax1.set_title('Заказы и выручка по месяцам', fontsize=13,
                  fontweight='bold', pad=15)
    ax1.set_xlabel('Месяц', fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.4, zorder=1)
    ax1.spines['top'].set_visible(False)

    # Объединённая легенда
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', fontsize=9)

    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    return _fig_to_response(fig)


def _fig_to_response(fig):
    """Конвертирует matplotlib figure в PNG HttpResponse."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')