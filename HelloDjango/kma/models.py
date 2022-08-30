from django.db import models

class DefaultWeb(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя веба', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Веб по умолчанию'
        verbose_name_plural = 'Вебы по умолчаниюа'


class PhoneNumber(models.Model):
    short = models.CharField(max_length=2, verbose_name='Код страны ISO', unique=True)
    phone = models.CharField(max_length=15, verbose_name='Валидный номер')
    ru_full_name = models.CharField(max_length=20, verbose_name='Русское название', blank=True, unique=True)
    phone_code = models.CharField(max_length=15, verbose_name='Моб код страны', blank=True)
    currency = models.CharField(max_length=5, verbose_name='Валюта', blank=True)
    words = models.JSONField(default={"words": [], "templates": []}, verbose_name='Слова под гео')
    langs = models.CharField(max_length=15, verbose_name='Языки гео', blank=True)

    class Meta:
        verbose_name = 'Валидный номер'
        verbose_name_plural = 'Валидные номера'

    @staticmethod
    def get_phone_code_by_country(iso_code):
        """Получить моб код по коду страны"""
        iso_code = iso_code.lower()
        try:
            phone = PhoneNumber.objects.get(short=iso_code)
            return phone.phone_code
        except PhoneNumber.DoesNotExist as error:
            return f'{iso_code}:{error}'

class Language(models.Model):
    iso = models.CharField(max_length=2, verbose_name='Код iso языка', primary_key=True)
    russian_name = models.CharField(max_length=25, verbose_name='Русское название', blank=True)

    class Meta:
        ordering = ['iso']

    def __str__(self):
        return f'{self.russian_name}({self.iso.upper()})'


class OfferPosition(models.Model):
    name = models.CharField(max_length=50, verbose_name='Оффер', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural= 'Офферы'



