import io
import os.path
from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.files.images import ImageFile
from ordered_model.models import OrderedModel
import requests as req
from requests.exceptions import RequestException
from PIL import Image


def get_file_size_text(size):
    kb = size // 1024
    if kb <= 1023:
        return f'{kb}kb'
    else:
        mb = round(kb // 1024, 2)
        return f'{mb}MB'


def remove_file_if_exists(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def load_img_http(url):
    result = {}
    result['status'] = False
    try:
        res = req.get(url)
        if res.status_code != 200:
            result['msg'] = 'status code ' + str(res.status_code)
        elif res.headers['Content-Type'] and not res.headers['Content-Type'].startswith('image'):
            result['msg'] = res.headers['Content-Type']
        else:
            result['status'] = True
            result['content'] = res.content
    except RequestException as error:
        result['msg'] = 'status code ' + str(error)
    return result


def make_thumb(image_path, size: tuple, compress=False):
    image = Image.open(image_path)
    image.thumbnail(size, reducing_gap=3.0)
    return image


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
        blank=True,
    )

    discount_type = models.CharField(
        max_length=20,
        verbose_name='Тип скидки',
        choices=DISCOUNT_TYPE,
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
        blank=True,
        verbose_name='Требует внимания'
    )
    filter = models.CharField(
        max_length=30,
        verbose_name='Прочий фильтр',
        default='',
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

    def save(self, **kwargs):
        if self.pk:
            super().save(**kwargs)
        else:
            super().save(**kwargs)
            actual_lists = ActualUserList.objects.all()
            for user_list in actual_lists:
                user_check_point = UserSiteCheckPoint(user_list=user_list, check_point=self)
                user_check_point.save()

    def __str__(self):
        return self.text

    @staticmethod
    def filter_check_points(land):
        checks = CheckPoint.objects.filter(
            Q(land_type__iexact=land.land_type) | Q(land_type__iexact=''),
            Q(discount_type__iexact=land.discount_type) | Q(discount_type__iexact=''),
            Q(for_geo__icontains=land.country) | Q(for_geo__iexact=''),
            Q(for_lang__icontains=land.language) | Q(for_lang__iexact=''),
            Q(filter__in=land.land_attrs) | Q(filter__iexact=''),
        )
        return checks


class ActualUserList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk}: {self.user}-{self.url}'

    class Meta:
        unique_together = ['user', 'url']
        ordering = ['-pk']

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
        except ActualUserList.DoesNotExist as error:
            user_list = ActualUserList.objects.create(user=user, url=url)
            check_points = CheckPoint.objects.all()
            user_check_points = []
            for check_point in check_points:
                obj = UserSiteCheckPoint(user_list=user_list,check_point=check_point)
                user_check_points.append(obj)
            UserSiteCheckPoint.objects.bulk_create(user_check_points)
        return user_list

    def create_thumbs_archive(self,img_qs):
        pass



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



def image_path(instanse, filename):
    domain_name = instanse.domain.url.replace('http://', '')
    return f'{domain_name}/{filename}'


class SiteImage(models.Model):
    domain = models.ForeignKey(ActualUserList, on_delete=models.CASCADE)
    image_url = models.URLField()
    page_width = models.IntegerField(blank=True, null=True)
    page_height = models.IntegerField(blank=True, null=True)
    orig_img = models.ImageField(blank=True, upload_to=image_path, )
    thumb = models.ImageField(blank=True, upload_to=image_path, )
    thumb_compress = models.ImageField(blank=True, upload_to=image_path, )

    class Meta:
        unique_together = ['domain', 'image_url']
        ordering = ['-pk']

    def orig_img_params(self):
        return self._image_info(self.orig_img)

    def thumb_params(self):
        return self._image_info(self.thumb)

    def delete_images(self):
        for field in self.orig_img, self.thumb:
            if field:
                remove_file_if_exists(field.path)
        self.orig_img = None
        self.thumb = None
        self.save()

    def load_orig_img(self, soft=False):
        self.delete_images()
        if soft and self.orig_img:
            return
        res = load_img_http(self.image_url)
        if res['status']:
            bytes = res['content']
            ext = os.path.splitext(self.image_url)[1]
            img = ImageFile(io.BytesIO(bytes), name=f'some{ext}')
            self.orig_img = img
            self.save()
            print(res['status'])
            return {'status': True}
        else:
            print(res)
            return res

    def ext(self):
        return os.path.splitext(self.orig_img.path)[1]

    def make_thumb(self, size=(50,50)):
        if self.orig_img:
            if self.thumb:
                remove_file_if_exists(self.thumb.path)
            # size = (self.page_width, self.page_height)
            # if not all(size):
            #     size = (50, 50)
            thumb = make_thumb(self.orig_img.path, size)
            blob = io.BytesIO()
            thumb.save(blob, thumb.format)
            ext = os.path.splitext(self.image_url)[1]
            self.thumb = ImageFile(blob, name=f'THUMB{ext}')
            self.save()

    def load_make_thumb(self):
        res_loading = self.load_orig_img()
        if res_loading['status']:
            self.make_thumb()
        return res_loading

    def compression_percent(self):
        if self.orig_img and self.thumb:
            return round(self.orig_img.size / self.thumb.size / 100, 1)

    def compression_weight(self):
        if self.orig_img and self.thumb:
            return self.orig_img.size - self.thumb.size

    def _image_info(self, field):
        if field:
            return {
                'size': field.size,
                'size_text': get_file_size_text(field.size),
                'width': field.width,
                'height': field.height,
                'file_name': os.path.basename(field.name),
            }
        return None



