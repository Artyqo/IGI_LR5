from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
import datetime

from .models import (
    Country, Hotel, Tour, Employee, Client,
    Order, Review, PromoCode, FAQ, Vacancy, News, CompanyInfo
)
from .models import phone_validator, validate_adult


class PhoneValidatorTest(TestCase):
    def test_valid_phone_29(self):
        try:
            phone_validator('+375 (29) 123-45-67')
        except ValidationError:
            self.fail('Валидный номер не прошёл валидацию')

    def test_valid_phone_33(self):
        try:
            phone_validator('+375 (33) 123-45-67')
        except ValidationError:
            self.fail('Валидный номер не прошёл валидацию')

    def test_invalid_phone_no_plus(self):
        with self.assertRaises(ValidationError):
            phone_validator('375 (29) 123-45-67')

    def test_invalid_phone_wrong_code(self):
        with self.assertRaises(ValidationError):
            phone_validator('+375 (28) 123-45-67')

    def test_invalid_phone_format(self):
        with self.assertRaises(ValidationError):
            phone_validator('+375 29 1234567')


class AgeValidatorTest(TestCase):
    def test_adult_passes(self):
        birth = datetime.date.today().replace(year=datetime.date.today().year - 20)
        try:
            validate_adult(birth)
        except ValidationError:
            self.fail('Совершеннолетний не прошёл валидацию')

    def test_minor_fails(self):
        birth = datetime.date.today().replace(year=datetime.date.today().year - 17)
        with self.assertRaises(ValidationError):
            validate_adult(birth)

    def test_exactly_18_passes(self):
        today = datetime.date.today()
        birth = today.replace(year=today.year - 18)
        try:
            validate_adult(birth)
        except ValidationError:
            self.fail('Ровно 18 лет не прошло валидацию')


class TourPriceTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='Тестовая страна',
            climate_winter='холодно',
            climate_spring='тепло',
            climate_summer='жарко',
            climate_autumn='прохладно',
        )
        self.hotel = Hotel.objects.create(
            country=self.country,
            name='Тестовый отель',
            stars=3,
            price_per_day=100.00,
        )

    def test_price_one_week(self):
        tour = Tour(hotel=self.hotel, title='Тест', duration_weeks=1,
                    departure_date=datetime.date.today())
        self.assertEqual(tour.price, 700)

    def test_price_two_weeks(self):
        tour = Tour(hotel=self.hotel, title='Тест', duration_weeks=2,
                    departure_date=datetime.date.today())
        self.assertEqual(tour.price, 1400)

    def test_price_four_weeks(self):
        tour = Tour(hotel=self.hotel, title='Тест', duration_weeks=4,
                    departure_date=datetime.date.today())
        self.assertEqual(tour.price, 2800)


class CountryHotelRelationTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='Испания',
            climate_winter='мягкий',
            climate_spring='тёплый',
            climate_summer='жаркий',
            climate_autumn='бархатный',
        )
        Hotel.objects.create(country=self.country, name='Отель 1', stars=4, price_per_day=120)
        Hotel.objects.create(country=self.country, name='Отель 2', stars=5, price_per_day=200)

    def test_country_has_hotels(self):
        self.assertEqual(self.country.hotels.count(), 2)

    def test_hotel_str(self):
        hotel = Hotel.objects.get(name='Отель 1')
        self.assertIn('Отель 1', str(hotel))


class PromoCodeTest(TestCase):
    def setUp(self):
        PromoCode.objects.create(code='ACTIVE10', discount_amount=10, is_active=True)
        PromoCode.objects.create(code='OLD20', discount_amount=20, is_active=False)

    def test_active_promo(self):
        self.assertEqual(PromoCode.objects.filter(is_active=True).count(), 1)

    def test_archive_promo(self):
        self.assertEqual(PromoCode.objects.filter(is_active=False).count(), 1)

    def test_promo_str(self):
        promo = PromoCode.objects.get(code='ACTIVE10')
        self.assertIn('ACTIVE10', str(promo))
        self.assertIn('Активен', str(promo))

class ViewsPublicTest(TestCase):
    """Тесты публичных страниц — доступны всем без авторизации"""

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_news_page(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)

    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_page(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)

    def test_vacancies_page(self):
        response = self.client.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)

    def test_promocodes_page(self):
        response = self.client.get(reverse('promocodes'))
        self.assertEqual(response.status_code, 200)

    def test_reviews_page(self):
        response = self.client.get(reverse('reviews'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_page(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_tour_list_page(self):
        response = self.client.get(reverse('tour_list'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)


class ViewsAuthTest(TestCase):
    """Тесты доступа к защищённым страницам"""

    def setUp(self):
        # Обычный пользователь без роли
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )
        # Суперпользователь
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
        )

    def test_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login/?next=/profile/')

    def test_statistics_forbidden_for_guest(self):
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 403)

    def test_statistics_forbidden_for_regular_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 403)

    def test_statistics_accessible_for_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)

    def test_tour_create_forbidden_for_guest(self):
        response = self.client.get(reverse('tour_create'))
        self.assertEqual(response.status_code, 403)

    def test_tour_create_accessible_for_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('tour_create'))
        self.assertEqual(response.status_code, 200)

    def test_login_works(self):
        self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        # Проверяем что пользователь залогинен
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_works(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, '/')


class RegistrationTest(TestCase):
    """Тесты регистрации клиента"""

    def test_valid_registration(self):
        response = self.client.post(reverse('register'), {
            'username':   'newclient',
            'last_name':  'Тестов',
            'first_name': 'Тест',
            'address':    'г. Минск, ул. Тестовая, 1',
            'phone':      '+375 (29) 999-88-77',
            'birth_date': '1990-01-01',
            'timezone':   'Europe/Minsk',
            'password1':  'StrongPass123!',
            'password2':  'StrongPass123!',
        })
        self.assertTrue(User.objects.filter(username='newclient').exists())
        self.assertTrue(Client.objects.filter(user__username='newclient').exists())

    def test_invalid_phone_rejected(self):
        response = self.client.post(reverse('register'), {
            'username':   'newclient2',
            'last_name':  'Тестов',
            'first_name': 'Тест',
            'address':    'г. Минск, ул. Тестовая, 1',
            'phone':      '89991234567',
            'birth_date': '1990-01-01',
            'timezone':   'Europe/Minsk',
            'password1':  'StrongPass123!',
            'password2':  'StrongPass123!',
        })
        self.assertFalse(User.objects.filter(username='newclient2').exists())

    def test_minor_rejected(self):
        response = self.client.post(reverse('register'), {
            'username':   'newclient3',
            'last_name':  'Тестов',
            'first_name': 'Тест',
            'address':    'г. Минск, ул. Тестовая, 1',
            'phone':      '+375 (29) 999-88-77',
            'birth_date': '2015-01-01',
            'timezone':   'Europe/Minsk',
            'password1':  'StrongPass123!',
            'password2':  'StrongPass123!',
        })
        self.assertFalse(User.objects.filter(username='newclient3').exists())

class TourViewsTest(TestCase):
    """Тесты каталога туров — фильтрация, поиск, детали"""

    def setUp(self):
        self.country = Country.objects.create(
            name='Тест страна',
            climate_winter='холодно',
            climate_spring='тепло',
            climate_summer='жарко',
            climate_autumn='прохладно',
        )
        self.hotel = Hotel.objects.create(
            country=self.country,
            name='Тест отель',
            stars=4,
            price_per_day=100.00,
        )
        self.tour = Tour.objects.create(
            hotel=self.hotel,
            title='Тестовый тур',
            duration_weeks=1,
            departure_date=datetime.date.today() + datetime.timedelta(days=10),
            is_hot=False,
        )

    def test_tour_list_returns_tours(self):
        response = self.client.get(reverse('tour_list'))
        self.assertContains(response, 'Тестовый тур')

    def test_tour_detail(self):
        response = self.client.get(reverse('tour_detail', args=[self.tour.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый тур')

    def test_tour_filter_by_country(self):
        response = self.client.get(reverse('tour_list'), {'country': self.country.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый тур')

    def test_tour_filter_by_stars(self):
        response = self.client.get(reverse('tour_list'), {'stars': 4})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый тур')

    def test_tour_filter_hot(self):
        response = self.client.get(reverse('tour_list'), {'is_hot': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Тестовый тур')

    def test_tour_search(self):
        response = self.client.get(reverse('tour_list'), {'q': 'Тестовый'})
        self.assertContains(response, 'Тестовый тур')

    def test_tour_search_no_results(self):
        response = self.client.get(reverse('tour_list'), {'q': 'несуществующий'})
        self.assertNotContains(response, 'Тестовый тур')

    def test_tour_sort_price_asc(self):
        response = self.client.get(reverse('tour_list'), {'sort': 'price_asc'})
        self.assertEqual(response.status_code, 200)

    def test_tour_delete_by_admin(self):
        admin = User.objects.create_superuser(
            username='admin2', password='adminpass123'
        )
        self.client.login(username='admin2', password='adminpass123')
        response = self.client.post(reverse('tour_delete', args=[self.tour.pk]))
        self.assertRedirects(response, reverse('tour_list'))
        self.assertFalse(Tour.objects.filter(pk=self.tour.pk).exists())

    def test_tour_delete_forbidden_for_guest(self):
        response = self.client.post(reverse('tour_delete', args=[self.tour.pk]))
        self.assertEqual(response.status_code, 403)


class ProfileViewTest(TestCase):
    """Тесты личного кабинета для разных ролей"""

    def setUp(self):
        self.country = Country.objects.create(
            name='Профиль страна',
            climate_winter='х', climate_spring='т',
            climate_summer='ж', climate_autumn='п',
        )
        self.hotel = Hotel.objects.create(
            country=self.country, name='Профиль отель',
            stars=3, price_per_day=50.00,
        )
        # Клиент
        self.client_user = User.objects.create_user(
            username='client_user', password='pass123'
        )
        self.client_profile = Client.objects.create(
            user=self.client_user,
            last_name='Тестов', first_name='Клиент',
            address='г. Минск', phone='+375 (29) 111-11-11',
            birth_date=datetime.date(1990, 1, 1),
            timezone='Europe/Minsk',
        )
        # Сотрудник
        self.emp_user = User.objects.create_user(
            username='emp_user', password='pass123'
        )
        self.employee = Employee.objects.create(
            user=self.emp_user,
            full_name='Тестов Сотрудник',
            position='Менеджер',
            phone='+375 (29) 222-22-22',
            birth_date=datetime.date(1985, 5, 10),
            email='emp@test.by',
        )
        # Админ
        self.admin_user = User.objects.create_superuser(
            username='admin3', password='adminpass123'
        )

    def test_client_profile_accessible(self):
        self.client.login(username='client_user', password='pass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Клиент')

    def test_employee_profile_accessible(self):
        self.client.login(username='emp_user', password='pass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестов Сотрудник')

    def test_admin_profile_accessible(self):
        self.client.login(username='admin3', password='adminpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_user_without_role_redirected(self):
        bare_user = User.objects.create_user(
            username='bare_user', password='pass123'
        )
        self.client.login(username='bare_user', password='pass123')
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, reverse('index'))


class ReviewsTest(TestCase):
    """Тесты отзывов"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username='reviewer', password='pass123'
        )
        self.client_profile = Client.objects.create(
            user=self.client_user,
            last_name='Отзывов', first_name='Тест',
            address='г. Минск', phone='+375 (29) 333-33-33',
            birth_date=datetime.date(1990, 1, 1),
            timezone='Europe/Minsk',
        )

    def test_guest_cannot_post_review(self):
        response = self.client.post(reverse('reviews'), {
            'author_name': 'Гость',
            'text': 'Отличный отдых!',
            'rating': 5,
        })
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(Review.objects.count(), 0)

    def test_client_can_post_review(self):
        self.client.login(username='reviewer', password='pass123')
        response = self.client.post(reverse('reviews'), {
            'author_name': 'reviewer',
            'text': 'Отличный отдых был!',
            'rating': 5,
        })
        self.assertRedirects(response, reverse('reviews'))
        self.assertEqual(Review.objects.count(), 1)

    def test_review_saved_correctly(self):
        self.client.login(username='reviewer', password='pass123')
        self.client.post(reverse('reviews'), {
            'author_name': 'reviewer',
            'text': 'Прекрасное путешествие!',
            'rating': 4,
        })
        review = Review.objects.first()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.text, 'Прекрасное путешествие!')