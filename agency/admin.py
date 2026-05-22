from django.contrib import admin
from .models import News, CompanyInfo, FAQ, Vacancy, Review, PromoCode, Country, Hotel, Employee, Client, Tour, Order

# Настройка встроенного (Inline) редактирования
class HotelInline(admin.TabularInline):
    model = Hotel
    extra = 1  # Количество пустых строк для добавления новых отелей прямо внутри страны

class TourInline(admin.TabularInline):
    model = Tour
    extra = 1  # Количество пустых строк для добавления туров прямо внутри отеля

# Кастомизация отображения моделей

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'climate_summer', 'climate_winter')
    search_fields = ('name',)
    inlines = [HotelInline]  # Встраиваем отели в страницу страны!

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'stars', 'price_per_day')
    list_filter = ('country', 'stars')
    search_fields = ('name',)
    inlines = [TourInline]   # Встраиваем путевки в страницу отеля!

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'hotel', 'duration_weeks', 'departure_date', 'is_hot')
    list_filter = ('duration_weeks', 'is_hot', 'hotel__country')
    search_fields = ('title',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'employee', 'created_at', 'total_cost')
    list_filter = ('created_at', 'employee')
    # Позволяет удобно выбирать путевки в режиме ManyToMany через горизонтальный фильтр
    filter_horizontal = ('tours',)

# Регистрация остальных базовых моделей
admin.site.register(News)
admin.site.register(CompanyInfo)
admin.site.register(FAQ)
admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(PromoCode)
admin.site.register(Employee)
admin.site.register(Client)