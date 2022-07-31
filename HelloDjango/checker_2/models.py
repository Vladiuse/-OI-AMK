from django.db import models
from ordered_model.models import OrderedModel

# Create your models here.

class CheckPoint(models.Model):
    LAND_TYPES = ('land', 'Лэндинг'), ('preland', 'Прэлендинг')
    DISCOUNT_TYPE = ('free', 'Бесплатно'), ('low_price', 'Лоу-прайс')
    text = models.CharField(max_length=255, verbose_name='Описание пункта проверки')
    land_type = models.CharField(
        max_length=20,
        verbose_name='Тип сайта',
        choices=LAND_TYPES,
        null=True,
        blank=True,
    )

    discount_type = models.CharField(
        max_length=20,
        verbose_name='Тип скидки',
        choices=DISCOUNT_TYPE,
        null=True,
        blank=True,
    )
    for_geo = models.CharField(
        max_length=255,
        verbose_name='Только для гео',
        blank=True,
    )
    for_lang = models.CharField(
        max_length=255,
        verbose_name='Только для языка',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пункт проверки'
        verbose_name_plural = 'Пункты проверки'

    def __str__(self):
        return self.text


class Main(OrderedModel):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['order']


class Sub(OrderedModel):
    name = models.CharField(max_length=50)
    main = models.ForeignKey(Main, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']

