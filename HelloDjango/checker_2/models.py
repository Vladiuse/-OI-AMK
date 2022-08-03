from django.db import models
from ordered_model.models import OrderedModel

# Create your models here.
class CheckBlock(OrderedModel):
    name = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Блок проверки'
        verbose_name_plural = 'Блоки проверки'
        ordering = ['order']

    def __str__(self):
        return self.name
class CheckPoint(OrderedModel):
    LAND_TYPES = ('land', 'Лэндинг'), ('preland', 'Прэлендинг')
    DISCOUNT_TYPE = ('free', 'Бесплатно'), ('low_price', 'Лоу-прайс')

    text = models.CharField(max_length=255, verbose_name='Описание пункта проверки')
    parent = models.ForeignKey(CheckBlock, on_delete=models.CASCADE)
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
        ordering = ['order']

    def __str__(self):
        return self.text


