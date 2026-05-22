from django.db import migrations
from django.utils import timezone
import datetime


def populate_rich_data(apps, schema_editor):
    User        = apps.get_model('auth', 'User')
    CompanyInfo = apps.get_model('agency', 'CompanyInfo')
    News        = apps.get_model('agency', 'News')
    FAQ         = apps.get_model('agency', 'FAQ')
    Vacancy     = apps.get_model('agency', 'Vacancy')
    PromoCode   = apps.get_model('agency', 'PromoCode')
    Country     = apps.get_model('agency', 'Country')
    Hotel       = apps.get_model('agency', 'Hotel')
    Employee    = apps.get_model('agency', 'Employee')
    Client      = apps.get_model('agency', 'Client')
    Tour        = apps.get_model('agency', 'Tour')
    Order       = apps.get_model('agency', 'Order')
    Review      = apps.get_model('agency', 'Review')

    now = timezone.now()

    # =========================================================
    # О КОМПАНИИ
    # =========================================================
    CompanyInfo.objects.create(
        text=(
            "«Глобус Тревел» — туристическое агентство полного цикла, работающее на рынке с 2010 года. "
            "За это время мы организовали более 15 000 поездок в 60 стран мира и стали одним из "
            "наиболее востребованных агентств Минска. Наши специалисты подберут тур под любой бюджет: "
            "от бюджетного пляжного отдыха до индивидуального VIP-маршрута. "
            "Мы работаем напрямую с ведущими туроператорами и отельными цепочками, что позволяет "
            "предлагать клиентам лучшие цены без лишних наценок."
        )
    )

    # =========================================================
    # НОВОСТИ
    # =========================================================
    News.objects.create(
        title="Раннее бронирование 2026: скидки до 30%",
        short_description="Успейте забронировать лучшие отели на лето по ценам ушедшего зимнего сезона.",
        content=(
            "Стартовала ежегодная программа раннего бронирования туров. До конца месяца доступны "
            "эксклюзивные скидки на пятизвёздочные отели в партнёрстве с ведущими мировыми "
            "авиакомпаниями. Бронируйте сейчас — платите по старым ценам."
        ),
        published_date=now,
    )
    News.objects.create(
        title="Открытие сезона в Испании",
        short_description="Испанские курорты объявляют о готовности принять рекордное число туристов.",
        content=(
            "Испанские прибрежные зоны полностью обновили и подготовили инфраструктуру к летнему сезону. "
            "Ожидаются новые прямые рейсы из Минска и специальные семейные программы на Коста-Брава и Майорке."
        ),
        published_date=now - datetime.timedelta(days=1),
    )
    News.objects.create(
        title="Обновление правил оформления шенгенских виз",
        short_description="Сроки рассмотрения документов для туристических виз увеличились до 15 дней.",
        content=(
            "Консульства стран Европейского союза обновили регламент обработки анкет. "
            "Рекомендуем подавать документы не менее чем за месяц до вылета. "
            "Наши визовые специалисты помогут собрать полный пакет документов."
        ),
        published_date=now - datetime.timedelta(days=2),
    )
    News.objects.create(
        title="Топ-3 направления для экзотического отдыха этой весной",
        short_description="Мальдивы, Шри-Ланка и Таиланд бьют рекорды популярности среди наших клиентов.",
        content=(
            "Аналитический отдел «Глобус Тревел» подвёл итоги квартала: спрос на азиатские направления "
            "вырос на 45% благодаря упрощению въездного режима и отмене ПЦР-тестов."
        ),
        published_date=now - datetime.timedelta(days=3),
    )
    News.objects.create(
        title="Запуск программы лояльности «Глобус Клуб»",
        short_description="Копите бонусные баллы за каждую поездку и оплачивайте ими до 15% стоимости туров.",
        content=(
            "Мы рады объявить о запуске клубной системы для постоянных путешественников. "
            "Карта лояльности оформляется бесплатно при первом бронировании. "
            "Баллы начисляются с каждой покупки и не сгорают в течение трёх лет."
        ),
        published_date=now - datetime.timedelta(days=4),
    )

    News.objects.create(
        title="Безвизовые направления 2026: куда поехать без хлопот",
        short_description="Составили список стран, доступных белорусам без визы в этом году.",
        content="Список безвизовых направлений для граждан Беларуси в 2026 году пополнился. "
                "Турция, Египет, Таиланд, Куба и ряд балканских стран по-прежнему доступны без визы. "
                "Наши менеджеры помогут подобрать маршрут под ваш бюджет и сроки.",
        published_date=now - datetime.timedelta(days=5),
    )
    News.objects.create(
        title="Горящие туры июня: успей забронировать",
        short_description="Остатки мест на июньские рейсы в Турцию и Грецию по специальным ценам.",
        content="В июне открываются горящие предложения на популярные направления. "
                "Белек, Анталья, Родос и Крит — от 850 BYN на двоих с перелётом и питанием. "
                "Количество мест ограничено, бронируйте прямо сейчас.",
        published_date=now - datetime.timedelta(days=6),
    )
    News.objects.create(
        title="Как правильно выбрать отель: советы эксперта",
        short_description="Разбираем на что смотреть при выборе отеля чтобы не разочароваться.",
        content="Звёзды отеля — не единственный критерий выбора. Расположение, тип питания, "
                "инфраструктура пляжа и отзывы реальных туристов не менее важны. "
                "Наши эксперты подготовили подробный гид по выбору идеального размещения.",
        published_date=now - datetime.timedelta(days=7),
    )
    News.objects.create(
        title="Страховка для путешественников: что нужно знать",
        short_description="Объясняем зачем нужна туристическая страховка и как её выбрать.",
        content="Медицинская страховка — обязательный документ для большинства стран. "
                "Мы сотрудничаем с ведущими страховыми компаниями и оформляем полисы "
                "прямо при покупке тура. Стоимость от 5 BYN в сутки.",
        published_date=now - datetime.timedelta(days=8),
    )
    News.objects.create(
        title="Семейный отдых: топ-5 курортов для детей",
        short_description="Выбрали лучшие направления для отдыха с детьми по соотношению цена-качество.",
        content="Семейный туризм требует особого подхода: анимация, детские бассейны, "
                "мелководье и развлекательная инфраструктура. Египет, Турция и Греция "
                "традиционно лидируют в нашем рейтинге семейных направлений.",
        published_date=now - datetime.timedelta(days=9),
    )

    # =========================================================
    # FAQ
    # =========================================================
    FAQ.objects.create(
        question="Что такое «горящий тур»?",
        answer=(
            "Путёвка, продаваемая по сниженной цене ближе к дате вылета из-за нераспроданных мест "
            "на авиарейсе или в отеле. Скидка может достигать 40–60% от первоначальной стоимости."
        ),
    )
    FAQ.objects.create(
        question="Что включает система All Inclusive?",
        answer=(
            "Режим обслуживания, при котором трёхразовое питание, лёгкие закуски, большинство напитков "
            "и развлечения входят в стоимость проживания. Конкретный перечень услуг уточняйте в описании отеля."
        ),
    )
    FAQ.objects.create(
        question="Что такое трансфер в туризме?",
        answer=(
            "Заранее забронированная перевозка пассажиров из аэропорта до отеля и обратно. "
            "Трансфер может быть индивидуальным (только ваша группа) или групповым (с другими туристами)."
        ),
    )
    FAQ.objects.create(
        question="Нужна ли виза в Египет?",
        answer=(
            "Гражданам Беларуси для въезда в Египет требуется виза. Её можно оформить заранее в "
            "консульстве или получить по прилёту (Visa on Arrival) стоимостью около 25 USD. "
            "Наше агентство поможет с оформлением заранее."
        ),
    )
    FAQ.objects.create(
        question="Можно ли оплатить тур в рассрочку?",
        answer=(
            "Да. Мы предлагаем рассрочку на срок до 6 месяцев без процентов совместно с банками-партнёрами. "
            "Для оформления достаточно паспорта и первоначального взноса от 30% стоимости тура."
        ),
    )
    FAQ.objects.create(
        question="Что такое система HB (Half Board)?",
        answer="Полупансион — режим питания, включающий завтрак и ужин. "
               "Обед в стоимость не входит и оплачивается отдельно в ресторане отеля или за его пределами.",
    )
    FAQ.objects.create(
        question="За сколько дней до вылета нужно оформлять тур?",
        answer="Стандартный тур рекомендуется бронировать за 2–4 недели до вылета. "
               "Горящие туры оформляются за 3–7 дней. Визовые направления требуют "
               "подачи документов минимум за 2–3 недели.",
    )
    FAQ.objects.create(
        question="Что такое чартерный рейс?",
        answer="Нерегулярный авиарейс, организованный туроператором специально для перевозки туристов. "
               "Как правило дешевле регулярных рейсов, но менее гибкий по расписанию.",
    )
    FAQ.objects.create(
        question="Можно ли изменить дату вылета после бронирования?",
        answer="Изменение даты вылета возможно, но сопровождается штрафными санкциями со стороны "
               "авиакомпании и туроператора. Рекомендуем уточнять условия изменения до оплаты тура.",
    )
    FAQ.objects.create(
        question="Что входит в стоимость путевки?",
        answer="Стандартная путёвка включает перелёт туда и обратно, трансфер аэропорт–отель–аэропорт, "
               "проживание в отеле и питание согласно выбранному режиму. "
               "Экскурсии, страховка и виза оплачиваются отдельно если не указано иное.",
    )

    # =========================================================
    # ВАКАНСИИ
    # =========================================================
    Vacancy.objects.create(
        title="Менеджер по туризму",
        description=(
            "Консультирование клиентов по направлениям и подбор туров под запрос. "
            "Оформление бронирований, работа с туроператорами и авиакассами. "
            "Опыт в туризме от 1 года. Знание английского — обязательно, "
            "знание второго иностранного языка приветствуется."
        ),
        salary="1 600 BYN + % от личных продаж",
    )
    Vacancy.objects.create(
        title="Старший менеджер по VIP-туризму",
        description=(
            "Ведение ключевых клиентов агентства: индивидуальные маршруты, яхтенные туры, "
            "организация деловых поездок и MICE-мероприятий. Опыт работы от 3 лет обязателен. "
            "Требуется свободное владение английским и уверенное — немецким или французским."
        ),
        salary="2 400 BYN + премии",
    )
    Vacancy.objects.create(
        title="Визовый специалист",
        description=(
            "Подготовка и подача документов на шенгенские, американские и азиатские визы. "
            "Консультирование клиентов по визовым требованиям разных стран. "
            "Внимательность, усидчивость и опыт работы с документами — обязательны."
        ),
        salary="1 400 BYN",
    )
    Vacancy.objects.create(
        title="SMM-специалист / Контент-менеджер",
        description=(
            "Ведение социальных сетей агентства (Instagram, Telegram, VK). "
            "Создание фото- и видеоконтента, написание текстов о направлениях и акциях. "
            "Опыт работы с таргетированной рекламой и аналитикой — преимущество."
        ),
        salary="1 300 BYN",
    )
    Vacancy.objects.create(
        title="Менеджер по работе с корпоративными клиентами",
        description="Организация деловых поездок и MICE-мероприятий для корпоративных заказчиков. "
                    "Ведение переговоров, составление коммерческих предложений. "
                    "Опыт в B2B-продажах от 2 лет.",
        salary="2 000 BYN + бонусы",
    )
    Vacancy.objects.create(
        title="Бухгалтер",
        description="Ведение первичной документации, работа с туроператорами по взаиморасчётам, "
                    "подготовка отчётности. Знание 1С обязательно. Опыт в туризме — преимущество.",
        salary="1 500 BYN",
    )
    Vacancy.objects.create(
        title="Администратор офиса",
        description="Встреча клиентов, входящие звонки, работа с документами и оргтехникой. "
                    "Приятная внешность, грамотная речь, уверенный пользователь ПК. "
                    "Опыт работы от 6 месяцев.",
        salary="1 200 BYN",
    )
    Vacancy.objects.create(
        title="Гид-переводчик (английский/испанский)",
        description="Сопровождение туристических групп за рубежом, проведение экскурсий. "
                    "Свободное владение английским и испанским языками обязательно. "
                    "Готовность к командировкам до 20 дней в месяц.",
        salary="1 800 BYN + суточные",
    )
    Vacancy.objects.create(
        title="Специалист по работе с претензиями",
        description="Рассмотрение жалоб и претензий клиентов, взаимодействие с туроператорами "
                    "и страховыми компаниями. Стрессоустойчивость и юридическая грамотность — обязательны.",
        salary="1 450 BYN",
    )
    Vacancy.objects.create(
        title="IT-специалист / Системный администратор",
        description="Поддержка работы офисной инфраструктуры, сайта и CRM-системы агентства. "
                    "Администрирование серверов, настройка сетевого оборудования. "
                    "Опыт от 1 года, знание Linux приветствуется.",
        salary="1 700 BYN",
    )

    # =========================================================
    # ПРОМОКОДЫ
    # =========================================================
    PromoCode.objects.create(code="SUMMER2026",  discount_amount=10, is_active=True)
    PromoCode.objects.create(code="WELCOME5",    discount_amount=5,  is_active=True)
    PromoCode.objects.create(code="GLOBUSCLUB",  discount_amount=7,  is_active=True)
    PromoCode.objects.create(code="EARLYBIRD15", discount_amount=15, is_active=True)
    PromoCode.objects.create(code="WINTER2025",  discount_amount=15, is_active=False)
    PromoCode.objects.create(code="SPRING2025",  discount_amount=8,  is_active=False)

    # =========================================================
    # СОТРУДНИКИ
    # =========================================================
    u_dir  = User.objects.create(username="ivanov_director", is_staff=True)
    u_emp1 = User.objects.create(username="kovaleva_anna",   is_staff=True)
    u_emp2 = User.objects.create(username="sokolov_dmitry",  is_staff=True)
    u_emp3 = User.objects.create(username="melnik_elena",    is_staff=True)

    Employee.objects.create(
        user=u_dir,
        full_name="Иванов Сергей Михайлович",
        position="Директор агентства",
        phone="+375 (29) 100-00-01",
        birth_date=datetime.date(1978, 4, 12),
        email="ivanov@globustravel.by",
    )
    Employee.objects.create(
        user=u_emp1,
        full_name="Ковалёва Анна Дмитриевна",
        position="Ведущий менеджер по Европе",
        phone="+375 (29) 200-11-22",
        birth_date=datetime.date(1993, 7, 19),
        email="kovaleva@globustravel.by",
    )
    Employee.objects.create(
        user=u_emp2,
        full_name="Соколов Дмитрий Александрович",
        position="Эксперт по экзотическим направлениям",
        phone="+375 (29) 300-22-33",
        birth_date=datetime.date(1989, 11, 5),
        email="sokolov@globustravel.by",
    )
    Employee.objects.create(
        user=u_emp3,
        full_name="Мельник Елена Викторовна",
        position="Визовый специалист",
        phone="+375 (33) 400-33-44",
        birth_date=datetime.date(1995, 2, 28),
        email="melnik@globustravel.by",
    )

    # =========================================================
    # СТРАНЫ
    # =========================================================
    spain = Country.objects.create(
        name="Испания",
        climate_winter="Мягкий, +10…+15°C, дожди на севере",
        climate_spring="Тёплый, +18…+22°C, цветение",
        climate_summer="Жаркий и сухой, +28…+35°C",
        climate_autumn="Бархатный сезон, +20…+25°C",
    )
    egypt = Country.objects.create(
        name="Египет",
        climate_winter="Комфортный, +18…+23°C, почти без осадков",
        climate_spring="Тёплый, +25…+30°C",
        climate_summer="Очень жаркий и сухой, +35…+42°C",
        climate_autumn="Идеальный, +26…+32°C",
    )
    italy = Country.objects.create(
        name="Италия",
        climate_winter="Прохладный, +5…+12°C, дожди",
        climate_spring="Солнечный, +15…+22°C",
        climate_summer="Жаркий, +27…+33°C",
        climate_autumn="Мягкий, +17…+23°C",
    )
    turkey = Country.objects.create(
        name="Турция",
        climate_winter="Мягкий, +8…+14°C на побережье",
        climate_spring="Тёплый, +18…+24°C",
        climate_summer="Жаркий, +30…+38°C",
        climate_autumn="Тёплый, +22…+28°C",
    )
    greece = Country.objects.create(
        name="Греция",
        climate_winter="Прохладный, +8…+14°C",
        climate_spring="Приятный, +16…+23°C",
        climate_summer="Солнечный и жаркий, +28…+35°C",
        climate_autumn="Тёплый, +20…+26°C",
    )

    # =========================================================
    # ОТЕЛИ (12 штук — по 2–3 на страну)
    # =========================================================
    # Испания
    h1  = Hotel.objects.create(country=spain,  name="Gran Meliá Palacio de Isora", stars=5, price_per_day=210.00)
    h2  = Hotel.objects.create(country=spain,  name="Playa Sol Mallorca",          stars=4, price_per_day=115.00)
    h3  = Hotel.objects.create(country=spain,  name="Regency Barcelona Centre",    stars=3, price_per_day=72.00)
    # Египет
    h4  = Hotel.objects.create(country=egypt,  name="Albatros Palace Resort",      stars=5, price_per_day=135.00)
    h5  = Hotel.objects.create(country=egypt,  name="Sea Gull Beach Resort",       stars=4, price_per_day=88.00)
    h6  = Hotel.objects.create(country=egypt,  name="Desert Rose Resort",          stars=5, price_per_day=148.00)
    # Италия
    h7  = Hotel.objects.create(country=italy,  name="Rome Cavalieri Waldorf",      stars=5, price_per_day=230.00)
    h8  = Hotel.objects.create(country=italy,  name="Venezia Palazzo Barbarigo",   stars=4, price_per_day=165.00)
    h9  = Hotel.objects.create(country=italy,  name="Milano Navigli Boutique",     stars=3, price_per_day=92.00)
    # Турция
    h10 = Hotel.objects.create(country=turkey, name="Rixos Premium Belek",         stars=5, price_per_day=195.00)
    h11 = Hotel.objects.create(country=turkey, name="Club Asteria Belek",          stars=4, price_per_day=105.00)
    # Греция
    h12 = Hotel.objects.create(country=greece, name="Mykonos Grand Hotel & Resort",stars=5, price_per_day=245.00)

    # =========================================================
    # ПУТЁВКИ (12 штук)
    # =========================================================
    t1  = Tour.objects.create(hotel=h1,  title="Тенерифе: Атлантика на ладони",      duration_weeks=2, departure_date=datetime.date(2026, 7, 5),  is_hot=True)
    t2  = Tour.objects.create(hotel=h2,  title="Солнечная Майорка",                  duration_weeks=1, departure_date=datetime.date(2026, 6, 14), is_hot=False)
    t3  = Tour.objects.create(hotel=h3,  title="Барселона — город Гауди",            duration_weeks=1, departure_date=datetime.date(2026, 5, 30), is_hot=False)
    t4  = Tour.objects.create(hotel=h4,  title="Хургада Премиум — семейный отдых",   duration_weeks=4, departure_date=datetime.date(2026, 9, 7),  is_hot=False)
    t5  = Tour.objects.create(hotel=h5,  title="Доступный Египет: море и пирамиды", duration_weeks=2, departure_date=datetime.date(2026, 5, 24), is_hot=True)
    t6  = Tour.objects.create(hotel=h6,  title="Шарм-эль-Шейх: коралловый рай",     duration_weeks=2, departure_date=datetime.date(2026, 7, 12), is_hot=False)
    t7  = Tour.objects.create(hotel=h7,  title="Римские каникулы",                  duration_weeks=1, departure_date=datetime.date(2026, 10, 9), is_hot=False)
    t8  = Tour.objects.create(hotel=h8,  title="Огни Венеции",                      duration_weeks=2, departure_date=datetime.date(2026, 6, 20), is_hot=False)
    t9  = Tour.objects.create(hotel=h9,  title="Уикенд в Милане",                   duration_weeks=1, departure_date=datetime.date(2026, 11, 1), is_hot=True)
    t10 = Tour.objects.create(hotel=h10, title="Белек: всё включено у моря",        duration_weeks=2, departure_date=datetime.date(2026, 6, 28), is_hot=True)
    t11 = Tour.objects.create(hotel=h11, title="Анталья — бюджетный пляжный отдых", duration_weeks=1, departure_date=datetime.date(2026, 8, 10), is_hot=False)
    t12 = Tour.objects.create(hotel=h12, title="Миконос: греческие острова",        duration_weeks=2, departure_date=datetime.date(2026, 8, 22), is_hot=False)

    # =========================================================
    # КЛИЕНТЫ (12 человек с реальными белорусскими именами)
    # =========================================================
    def make_client(username, last, first, middle, address, phone, birth):
        u = User.objects.create(username=username)
        return Client.objects.create(
            user=u, last_name=last, first_name=first, middle_name=middle,
            address=address, phone=phone, birth_date=birth,
        )

    c1  = make_client("zhukova_marina",    "Жукова",      "Марина",    "Игоревна",    "г. Минск, ул. Притыцкого, д. 12, кв. 45",     "+375 (29) 511-22-01", datetime.date(1990, 3, 14))
    c2  = make_client("bondar_alexey",     "Бондарь",     "Алексей",   "Николаевич",  "г. Минск, пр. Независимости, д. 87, кв. 3",   "+375 (29) 522-33-02", datetime.date(1985, 8, 22))
    c3  = make_client("karpova_olga",      "Карпова",     "Ольга",     "Сергеевна",   "г. Брест, ул. Советская, д. 5, кв. 18",        "+375 (29) 533-44-03", datetime.date(1994, 1, 7))
    c4  = make_client("lukashev_pavel",    "Лукашев",     "Павел",     "Андреевич",   "г. Гродно, ул. Ожешко, д. 22, кв. 9",         "+375 (33) 544-55-04", datetime.date(1988, 6, 30))
    c5  = make_client("savelyeva_tatyana", "Савельева",   "Татьяна",   "Владимировна","г. Минск, ул. Якубова, д. 34, кв. 77",         "+375 (29) 555-66-05", datetime.date(1997, 11, 3))
    c6  = make_client("golovin_roman",     "Головин",     "Роман",     "Евгеньевич",  "г. Витебск, ул. Замковая, д. 7, кв. 2",        "+375 (44) 566-77-06", datetime.date(1982, 4, 19))
    c7  = make_client("sidorova_natalya",  "Сидорова",    "Наталья",   "Петровна",    "г. Минск, ул. Маяковского, д. 15, кв. 31",     "+375 (29) 577-88-07", datetime.date(1991, 9, 25))
    c8  = make_client("trofimov_andrey",   "Трофимов",    "Андрей",    "Игоревич",    "г. Могилёв, ул. Первомайская, д. 44, кв. 6",   "+375 (33) 588-99-08", datetime.date(1987, 12, 11))
    c9  = make_client("vasilenko_darya",   "Василенко",   "Дарья",     "Олеговна",    "г. Минск, ул. Ленинградская, д. 3, кв. 50",    "+375 (29) 599-00-09", datetime.date(1999, 5, 8))
    c10 = make_client("nikitin_igor",      "Никитин",     "Игорь",     "Васильевич",  "г. Гомель, ул. Советская, д. 18, кв. 14",      "+375 (44) 610-11-10", datetime.date(1980, 7, 16))
    c11 = make_client("morozova_svetlana", "Морозова",    "Светлана",  "Юрьевна",     "г. Минск, пр. Победителей, д. 9, кв. 22",      "+375 (29) 621-22-11", datetime.date(1993, 2, 14))
    c12 = make_client("zaitsev_kirill",    "Зайцев",      "Кирилл",    "Романович",   "г. Минск, ул. Кальварийская, д. 7, кв. 88",    "+375 (29) 632-33-12", datetime.date(1996, 10, 2))

    # =========================================================
    # ЗАКАЗЫ (берём сотрудников из базы по username)
    # =========================================================
    emp_anna   = u_emp1.employee_set.first() if hasattr(u_emp1, 'employee_set') else Employee.objects.get(user=u_emp1)
    emp_dmitry = Employee.objects.get(user=u_emp2)
    emp_elena  = Employee.objects.get(user=u_emp3)

    def make_order(client, employee, tours_list):
        total = sum(t.hotel.price_per_day * (t.duration_weeks * 7) for t in tours_list)
        order = Order.objects.create(client=client, employee=employee, total_cost=total)
        order.tours.set(tours_list)
        return order

    make_order(c1,  emp_anna,   [t1])
    make_order(c2,  emp_anna,   [t2, t3])   # Майорка + Барселона
    make_order(c3,  emp_dmitry, [t4])
    make_order(c4,  emp_dmitry, [t5])
    make_order(c5,  emp_anna,   [t6])
    make_order(c6,  emp_dmitry, [t7])
    make_order(c7,  emp_anna,   [t8])
    make_order(c8,  emp_dmitry, [t9])
    make_order(c9,  emp_elena,  [t10])
    make_order(c10, emp_elena,  [t11])
    make_order(c11, emp_anna,   [t12])
    make_order(c12, emp_elena,  [t1, t10])  # Тенерифе + Белек

    # =========================================================
    # ОТЗЫВЫ (12 штук, разные оценки и живой текст)
    # =========================================================
    reviews_data = [
        (c1,  5, "Жукова Марина",
         "Отдыхали на Тенерифе — просто сказка. Номер с видом на океан, персонал внимателен к каждой мелочи. "
         "Анна подобрала идеальный вариант с первого раза, не пришлось ничего переделывать. Уже планируем следующую поездку!"),

        (c2,  4, "Бондарь Алексей",
         "Брали сразу два тура — Майорку и Барселону. Организация на высоте, всё чётко по расписанию. "
         "Единственный минус — стыковка в аэропорту оказалась короткой, немного нервничали. Но к агентству вопросов нет."),

        (c3,  5, "Карпова Ольга",
         "Египет на четыре недели — лучший отпуск в моей жизни. Отель Albatros Palace просто великолепен: "
         "огромная территория, несколько бассейнов, потрясающая еда. Дмитрий всё организовал безупречно."),

        (c4,  3, "Лукашев Павел",
         "В целом неплохо, но ожидал немного большего за эти деньги. Отель хороший, море чистое. "
         "Но трансфер задержался на полтора часа — это неприятно после длинного перелёта. "
         "Надеюсь, в следующий раз будет лучше."),

        (c5,  5, "Савельева Татьяна",
         "Шарм-эль-Шейх превзошёл все ожидания! Коралловые рифы прямо у берега, вода прозрачнейшая. "
         "Агентство порекомендовала подруга — теперь сама советую всем знакомым. Спасибо, Анна!"),

        (c6,  4, "Головин Роман",
         "Рим — это вечность. Три дня пролетели как один миг. Отель выбрали правильно: "
         "15 минут пешком до Колизея. Немного шумновато по ночам — но это же центр Рима, что поделаешь."),

        (c7,  5, "Сидорова Наталья",
         "Венеция — город-мечта. Плыть на гондоле по каналам на закате — незабываемо. "
         "Отель Palazzo Barbarigo — роскошь во всём: от интерьеров до завтрака. Рекомендую на все 100%."),

        (c8,  4, "Трофимов Андрей",
         "Взял тур в Милан спонтанно — и не пожалел. Хорошая цена, удобный отель рядом с навильи. "
         "Шопинг, галерея Виктора Эммануила, стейк с трюфелем — идеальный уикенд. Вернусь снова."),

        (c9,  5, "Василенко Дарья",
         "Турция, Белек, Rixos — это другой уровень. All inclusive здесь реально всё включено: "
         "от снорклинга до вечерних шоу. Елена отлично проконсультировала, подобрала именно то, что нужно."),

        (c10, 2, "Никитин Игорь",
         "Анталья понравилась, но отель оказался не совсем таким, как на фотографиях — номер меньше, "
         "вид не на море, а на парковку. Буду внимательнее читать описание в следующий раз. "
         "Претензий к агентству немного, но осадок остался."),

        (c11, 5, "Морозова Светлана",
         "Миконос — это не просто отдых, это эстетика. Белые домики, синие купола, закат над Эгейским морем... "
         "Отель Gran Meliá — выше всяких похвал. Персонал знает своё дело. Обязательно вернусь."),

        (c12, 4, "Зайцев Кирилл",
         "Брал сразу два тура — Тенерифе и Белек. Смелое решение, но не пожалел. "
         "Оба отеля на отличном уровне. Елена помогла выстроить логистику так, чтобы между турами "
         "был комфортный перерыв. Профессионал своего дела."),
    ]

    for client, rating, name, text in reviews_data:
        Review.objects.create(
            user=client.user,
            author_name=name,
            rating=rating,
            text=text,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(populate_rich_data),
    ]