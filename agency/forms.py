from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Client, Tour, phone_validator, validate_adult

import pytz
TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['hotel', 'title', 'duration_weeks', 'departure_date', 'is_hot']
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ClientRegistrationForm(UserCreationForm):
    last_name = forms.CharField(
        label="Фамилия",
        max_length=100,
    )
    first_name = forms.CharField(
        label="Имя",
        max_length=100,
    )
    middle_name = forms.CharField(
        label="Отчество",
        max_length=100,
        required=False,
    )
    address = forms.CharField(
        label="Адрес",
        max_length=255,
    )

    timezone = forms.ChoiceField(
        label="Ваша тайм-зона",
        choices=TIMEZONE_CHOICES,
        initial='Europe/Minsk',
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        help_text="Формат: +375 (29) XXX-XX-XX. Допустимые коды: 25, 29, 33, 44.",
        widget=forms.TextInput(attrs={'placeholder': '+375 (29) XXX-XX-XX'}),
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Регистрация доступна только клиентам 18+.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'last_name', 'first_name', 'middle_name',
            'address', 'phone', 'birth_date', 'timezone',
            'password1', 'password2',
        )

    def clean_phone(self):
        """Валидируем телефон напрямую через валидатор из модели."""
        phone = self.cleaned_data.get('phone', '').strip()
        try:
            phone_validator(phone)
        except ValidationError as e:
            raise ValidationError(e.message)
        return phone

    def clean_birth_date(self):
        """Валидируем возраст 18+ напрямую через валидатор из модели."""
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            try:
                validate_adult(birth_date)
            except ValidationError as e:
                raise ValidationError(e.message)
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Client.objects.create(
                user=user,
                last_name=self.cleaned_data['last_name'],
                first_name=self.cleaned_data['first_name'],
                middle_name=self.cleaned_data.get('middle_name') or '',
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date'],
                timezone=self.cleaned_data['timezone'],
            )
        return user