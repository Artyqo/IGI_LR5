from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^about/$', views.about, name='about'),
    re_path(r'^news/$', views.news_list, name='news_list'),
    re_path(r'^faq/$', views.faq_list, name='faq'),
    re_path(r'^vacancies/$', views.vacancy_list, name='vacancies'),
    re_path(r'^promocodes/$', views.promocode_list, name='promocodes'),
    re_path(r'^contacts/$', views.contacts_view, name='contacts'),
    re_path(r'^privacy/$', views.privacy_policy, name='privacy_policy'),
    re_path(r'^reviews/$', views.reviews, name='reviews'),
    re_path(r'^profile/$', views.profile_view, name='profile'),
    re_path(r'^statistics/$', views.statistics_view, name='statistics'),
    re_path(r'^charts/sales-by-country/$',  views.chart_sales_by_country, name='chart_sales_by_country'),
    re_path(r'^charts/tours-by-stars/$',    views.chart_tours_by_stars,   name='chart_tours_by_stars'),
    re_path(r'^charts/orders-by-month/$',   views.chart_orders_by_month,  name='chart_orders_by_month'),

    # CRUD для путевок с использованием регулярных выражений
    re_path(r'^tours/$', views.tour_list, name='tour_list'),
    re_path(r'^tours/(?P<pk>\d+)/$', views.tour_detail, name='tour_detail'),
    re_path(r'^tours/create/$', views.tour_create, name='tour_create'),
    re_path(r'^tours/(?P<pk>\d+)/update/$', views.tour_update, name='tour_update'),
    re_path(r'^tours/(?P<pk>\d+)/delete/$', views.tour_delete, name='tour_delete'),

    # Новый маршрут для покупки услуги/путевки зарегистрированным клиентом
    re_path(r'^tours/(?P<pk>\d+)/buy/$', views.tour_buy, name='tour_buy'),

    # Авторизация
    re_path(r'^login/$', views.login_view, name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^register/$', views.register_view, name='register'),
]