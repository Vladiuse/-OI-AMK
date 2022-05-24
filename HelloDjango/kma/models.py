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

    class Meta:
        verbose_name = 'Валидный номер'
        verbose_name_plural = 'Валидные номера'


class OfferPosition(models.Model):
    name = models.CharField(max_length=50, verbose_name='Оффер', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural= 'Офферы'



