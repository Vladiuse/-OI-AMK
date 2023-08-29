import zipfile
import io
import os.path
import random as r
from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.files.images import ImageFile
from ordered_model.models import OrderedModel
import requests as req
from requests.exceptions import RequestException
from PIL import Image,ImageOps
from urllib.parse import urlparse


def get_file_ext(file_path):
    return os.path.splitext(file_path)[1]

def get_file_size_text(size):
    kb = size // 1024
    if kb <= 1023:
        return f'{kb}kb'
    else:
        mb = round(kb // 1024, 2)
        return f'{mb}MB'

def _r():
    import string
    return ''.join(r.choices(string.ascii_uppercase,k=3))

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


def make_thumb(image_path, size: tuple):
    image = Image.open(image_path)
    pil = ImageOps.exif_transpose(image)
    image.thumbnail(size, reducing_gap=2.0)
    blob = io.BytesIO()
    image.save(blob, image.format, quality=95)
    ext = os.path.splitext(image_path)[1]
    thumb = ImageFile(blob, name=f'THUMB{_r()}{ext}')
    return thumb


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
    image_crop = models.BooleanField(default=True, verbose_name='показывать размеры картинок')

    def __str__(self):
        return f'{self.user}-{self.left_bar}-{self.click_elem}-{self.other}'



def image_path_site_image(instanse, filename):
    domain_name = instanse.domain.url.replace('http://', '')
    return f'{instanse.MEDIA_PATH}/{domain_name}/{filename}'


class SiteImage(models.Model):

    OVER_SIZE_BYTES = 300 * 1024
    OVER_SIZE_1000_BYTES = 150 * 1024

    MEDIA_PATH = 'site_images'
    OVER_300_KB = 'Больше 300kb'
    OVER_1000_PX = 'Больше 1000px'
    MAY_BE_CROP = 'Можно обрезать'

    domain = models.ForeignKey(ActualUserList, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=255)
    orig_img = models.ImageField(blank=True, upload_to=image_path_site_image, )
    thumb = models.ImageField(blank=True, upload_to=image_path_site_image, )
    thumb_compress = models.ImageField(blank=True, upload_to=image_path_site_image, )

    class Meta:
        unique_together = ['domain', 'image_url']
        ordering = ['-pk']

    def orig_img_params(self):
        return self._image_info(self.orig_img)

    # def thumb_params(self):
    #     return self._image_info(self.thumb)

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
            return {'status': True}
        else:
            return res

    def ext(self):
        return os.path.splitext(self.orig_img.path)[1]

    # def make_thumb(self, size=(50,50)):
    #     if self.orig_img:
    #         if self.thumb:
    #             remove_file_if_exists(self.thumb.path)
    #         thumb = make_thumb(self.orig_img.path, size)
    #         blob = io.BytesIO()
    #         thumb.save(blob, thumb.format)
    #         ext = os.path.splitext(str(self.image_url))[1]
    #         self.thumb = ImageFile(blob, name=f'THUMB{ext}')
    #         self.save()

    def load_make_thumb(self):
        res_loading = self.load_orig_img()
        if res_loading['status']:
            self.make_thumb()
        return res_loading
    #
    # def compression_percent(self):
    #     if self.orig_img and self.thumb:
    #         return round(self.orig_img.size / self.thumb.size / 100, 1)

    # def compression_weight(self):
    #     if self.orig_img and self.thumb:
    #         return self.orig_img.size - self.thumb.size

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

    def name_in_zip(self):
        img_name_in_zip = urlparse(self.image_url).path
        if urlparse(self.image_url).query:
             img_name_in_zip += '?' + urlparse(self.image_url).query
        return img_name_in_zip

    def is_over_size(self):
        if self.orig_img:
            if self.orig_img.size > SiteImage.OVER_SIZE_BYTES:
                return self.OVER_300_KB
            elif (self.orig_img.width > 1000 or self.orig_img.height > 1000) and self.orig_img.size >SiteImage.OVER_SIZE_1000_BYTES:
                return self.OVER_1000_PX
            else:
                return ''
        return ''

class CropTask(models.Model):
    domain = models.ForeignKey(ActualUserList, on_delete=models.CASCADE)
    archive = models.FileField(upload_to='_archive', blank=True)

    @staticmethod
    def create_crop_task(domain, qs, crop_data):
        task = CropTask.objects.create(domain=domain)
        crop_images = []
        files = []
        for site_image in qs:
            page_width = crop_data[str(site_image.pk)]['width']
            page_height = crop_data[str(site_image.pk)]['height']
            status_text = 's'
            crop_type = 'c'
            if site_image.is_over_size():
                status_text = site_image.is_over_size()
                crop_type = CropImage.OVER_SIZE
            else:
                status_text = SiteImage.MAY_BE_CROP
                crop_type = CropImage.NEED_CROP

            img_file = open(site_image.orig_img.path, 'rb')
            img_file_name = os.path.basename(site_image.orig_img.name)
            img = ImageFile(img_file, name=img_file_name)
            crop_image = CropImage(
                task=task,
                site_image=site_image,
                orig_img=img,
                page_width=page_width,
                page_height=page_height,
                thumb=make_thumb(site_image.orig_img.path, (page_width,page_height)),
                status_text=status_text,
                crop_type=crop_type,
            )
            crop_images.append(crop_image)
            files.append(img_file)
        CropImage.objects.bulk_create(crop_images)
        [file.close() for file in files]
        task.create_zip()
        return task

    def create_zip(self):
        crop_images = self.cropimage_set.select_related('site_image')
        zip_file_path = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_file_path, 'w')
        for image in crop_images:
            image_name_in_zip = image.site_image.name_in_zip()
            zip_file.write(image.thumb.path, image_name_in_zip)
        zip_file.close()
        self.archive.save('x.zip', zip_file_path)
        self.save()

    def files_size(self):
        images = self.cropimage_set.all()
        images = [img for img in images if img.is_thumb_optimized()]
        if images:
            images_size = sum(img.orig_img.size for img in images)
            thumbs_size = sum(img.thumb.size for img in images)
            diff_size = images_size - thumbs_size
            diff_percent = round((images_size-  thumbs_size )/ images_size*100 )
            return {
                'images_size': images_size,
                'thumb_size': thumbs_size,
                'diff_size': diff_size,
                'diff_percent': diff_percent,
            }
        return  {}


def image_path_crop_image(instanse, filename):
    return f'{instanse.MEDIA_PATH}/{instanse.task.pk}/{filename}'

class CropImage(models.Model):
    MEDIA_PATH = 'crop_images'
    OVER_SIZE = 'over_size'
    NEED_CROP = 'need_crop'
    CROP_TYPE = (
        (OVER_SIZE, OVER_SIZE),
        (NEED_CROP, NEED_CROP),
    )
    task = models.ForeignKey(CropTask, on_delete=models.CASCADE)
    site_image = models.ForeignKey(SiteImage, on_delete=models.CASCADE)
    orig_img = models.ImageField(upload_to=image_path_crop_image, )
    thumb = models.ImageField(blank=True, upload_to=image_path_crop_image, )
    compressed = models.ImageField(blank=True, upload_to=image_path_crop_image, )
    page_width = models.PositiveIntegerField()
    page_height = models.PositiveIntegerField()
    status_text = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=50, choices=CROP_TYPE, default='123')

    def is_thumb_optimized(self):
        return self.weight_diff_percent() > 20

    class Meta:
        ordering = ['-crop_type']

    def make_thumb(self, save=True):
        size = (self.page_width, self.page_height)
        if self.orig_img:
            if self.thumb:
                remove_file_if_exists(self.thumb.path)
            self.thumb = make_thumb(self.orig_img.path, size)
            if save:
                self.save()

    def page_compression(self):
        if self.orig_img:
            return round(self.orig_img.width / self.page_width,1)

    def weight_diff(self):
        if self.orig_img and self.thumb:
            return self.orig_img.size - self.thumb.size

    def weight_diff_percent(self):
        if self.orig_img and self.thumb:
            return round((self.orig_img.size - self.thumb.size) / self.orig_img.size * 100)


