from django.db import models
from ordered_model.models import OrderedModel
from django.contrib.auth.models import User

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
    is_notice = models.BooleanField(default=False, null=False, blank=True, verbose_name='Требует внимания')
    filter = models.CharField(max_length=30, verbose_name='Прочий фильтр', default='', null=False, blank=True)

    class Meta:
        verbose_name = 'Пункт проверки'
        verbose_name_plural = 'Пункты проверки'
        ordering = ['order']

    def __str__(self):
        return self.text



class UserSiteCheckPoint(models.Model):
    check_point = models.ForeignKey(CheckPoint, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=50)
    is_checked = models.BooleanField(default=False)


    class Meta:
        # verbose_name = 'Пункт проверки'
        # verbose_name_plural = 'Пункты проверки'
        ordering = ['check_point__order']
        unique_together = ['check_point', 'user', 'url']


    @staticmethod
    def make_user_url_list(user_model, url):
        """Создать чеклист проверки под конкрентый сайт и пользователя"""
        all = CheckPoint.objects.all()
        new_check_list = list()
        for check_point in all:
            u = UserSiteCheckPoint(check_point=check_point, user=user_model, url=url)
            new_check_list.append(u)
        new_list = UserSiteCheckPoint.objects.bulk_create(new_check_list)
        return new_list

    # def __str__(self):
    #     return self.text



