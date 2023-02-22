from django.db import models
from ordered_model.models import OrderedModel
from django.contrib.auth.models import User
from datetime import date, timedelta


# Create your models here.
class CheckBlock(OrderedModel):
    name = models.CharField(max_length=100, verbose_name='Название')
    manual_link = models.CharField(max_length=50, verbose_name='ссылка на доку', blank=True)

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
        # null=True,
        blank=True,
    )

    discount_type = models.CharField(
        max_length=20,
        verbose_name='Тип скидки',
        choices=DISCOUNT_TYPE,
        # null=True,
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
    is_notice = models.BooleanField(
        default=False,
        # null=False,
        blank=True,
        verbose_name='Требует внимания'
    )
    filter = models.CharField(
        max_length=30,
        verbose_name='Прочий фильтр',
        default='',
        # null=False,
        blank=True
    )
    manual_link = models.CharField(
        max_length=50,
        verbose_name='ссылка на доку',
        blank=True
    )

    class Meta:
        verbose_name = 'Пункт проверки'
        verbose_name_plural = 'Пункты проверки'
        ordering = ['order']

    def save(self):
        if self.pk:
            super().save()
        else:
            super().save()
            actual_lists = ActualUserList.objects.all()
            for user_list in actual_lists:
                user_check_point = UserSiteCheckPoint(user_list=user_list, check_point=self)
                user_check_point.save()

    def __str__(self):
        return self.text

    def full_info(self):
        print(self.text)
        print(self.land_type,self.discount_type,self.for_geo,self.for_lang,self.manual_link, sep=' | ')

class ActualUserList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=70)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'url']

    @staticmethod
    def dell_old():
        """Удалить старые записи чекера"""
        old = ActualUserList.objects.filter(date__lte=date.today() - timedelta(days=7))
        old.delete()
        return len(old)

    @staticmethod
    def get_or_create(user, url):
        try:
            user_list = ActualUserList.objects.get(user=user,url=url)
            print('GET')
        except ActualUserList.DoesNotExist as error:
            user_list = ActualUserList.objects.create(user=user, url=url)
            check_points = CheckPoint.objects.all()
            user_check_points = []
            for check_point in check_points:
                obj = UserSiteCheckPoint(user_list=user_list,check_point=check_point)
                user_check_points.append(obj)
            UserSiteCheckPoint.objects.bulk_create(user_check_points)
            print('CREATE')
        return user_list



class UserSiteCheckPoint(models.Model):
    check_point = models.ForeignKey(CheckPoint, on_delete=models.CASCADE)
    user_list = models.ForeignKey(ActualUserList, on_delete=models.CASCADE)
    is_checked = models.BooleanField(default=False)

    class Meta:
        ordering = ['check_point__order']
        unique_together = ['check_point', 'user_list']



class CheckerUserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    left_bar = models.BooleanField(default=True, verbose_name='Показывать боковую панель')
    click_elem = models.BooleanField(default=False, verbose_name='Показывать клик элементы')
    other = models.BooleanField(default=True, verbose_name='Показывать даты, формы')

    def __str__(self):
        return f'{self.user}-{self.left_bar}-{self.click_elem}-{self.other}'

