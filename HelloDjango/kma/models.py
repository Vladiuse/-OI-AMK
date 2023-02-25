from django.db import models
from django.contrib.auth.models import User

class DefaultWeb(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя веба', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Веб по умолчанию'
        verbose_name_plural = 'Вебы по умолчаниюа'


class Country(models.Model):
    iso = models.CharField(max_length=2, verbose_name='Код страны ISO', unique=True, primary_key=True)
    phone = models.CharField(max_length=15, verbose_name='Валидный номер')
    ru_full_name = models.CharField(max_length=20, verbose_name='Русское название', blank=True, unique=True)
    phone_code = models.CharField(max_length=15, verbose_name='Моб код страны', blank=True)
    currency = models.CharField(max_length=5, verbose_name='Валюта', blank=True)
    words = models.JSONField(default={"words": [], "templates": []}, verbose_name='Слова под гео')
    langs = models.CharField(max_length=15, verbose_name='Языки гео', blank=True)
    language = models.ManyToManyField('Language', blank=True)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    @staticmethod
    def get_phone_code_by_country(iso_code):
        """Получить моб код по коду страны"""
        iso_code = iso_code.lower()
        try:
            phone = Country.objects.get(short=iso_code)
            return phone.phone_code
        except Country.DoesNotExist as error:
            return f'{iso_code}:{error}'

    @staticmethod
    def get_country_phone(*countrys_iso)-> dict:
        """Возвразает словарь
        ключ:county_iso
        значение: номер телефона
        """
        phones = Country.objects.filter(short__in=countrys_iso).values()
        country_phone = dict()
        for p in phones:
            dic = {p['short']: p['phone']}
            country_phone.update(dic)
        return country_phone

class Language(models.Model):
    iso = models.CharField(max_length=2, verbose_name='Код iso языка', primary_key=True)
    russian_name = models.CharField(max_length=25, verbose_name='Русское название', blank=True)

    class Meta:
        ordering = ['iso']

    def __str__(self):
        return f'{self.russian_name}({self.iso.upper()})'


class OfferPosition(models.Model):
    name = models.CharField(max_length=50, verbose_name='Оффер', unique=True)


    def save(self):
        words = self.name.split(' ')
        for id, w in enumerate(words):
            words[id] = w.title()
        self.name = ' '.join(words)
        super().save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural= 'Офферы'

class UserApiKey(models.Model):

    token = models.CharField(max_length=40, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username



