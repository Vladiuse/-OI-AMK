from .models import SiteImage
from django.utils.html import mark_safe
import re
import os

from django.contrib import admin
from .models import CheckPoint, CheckBlock, CheckerUserSetting
from ordered_model.admin import OrderedModelAdmin


class CheckBlockAdmin(OrderedModelAdmin):
    list_display = ('id', 'name', 'move_up_down_links', 'manual_link', 'order',)
    list_display_links = ['id', 'name']


class CheckPointAdmin(OrderedModelAdmin):
    list_display = ['id', 'text', 'land_type', 'discount_type', 'for_geo', 'for_lang', 'move_up_down_links',
                    'is_notice', 'filter', 'manual_link', 'order']
    list_display_links = ['id', 'text']
    list_filter = ['parent__name']


class CheckerUserSettingAdmin(admin.ModelAdmin):
    list_display = ['user', 'left_bar', 'click_elem', 'other']
    list_display_links = ['user']


def img_tag(src):
    return mark_safe(f'<img src="{src}" width="50px" height="50px" style="background-color:#ffbaba;" />')


def remove_protokol(url: str):
    return re.sub('http[s]?://', '', url)


def load_image(modeladmin, request, queryset):
    for model in queryset:
        model.load_orig_img(soft=True)


class SiteImagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'domain', 'image_url_short', 'orig_img', 'orig_tag', 'thumb', 'thumb_tag']
    actions = [load_image, 'make_thumb', 'delete_images']
    list_filter = ['domain']

    @admin.action(description='Make Thumb')
    def make_thumb(self, request, queryset):
        for m in queryset:
            m.make_thumb()

    @admin.action(description='Delete images')
    def delete_images(self, request, queryset):
        for m in queryset:
            m.delete_images()

    def image_url_short(self, obj):
        return f'../{os.path.basename(obj.image_url)}'
        # return remove_protokol(obj.image_url)

    def orig_tag(self, obj):
        if obj.orig_img:
            return img_tag(obj.orig_img.url)

    def thumb_tag(self, obj):
        if obj.thumb:
            return img_tag(obj.thumb.url)


admin.site.register(SiteImage, SiteImagesAdmin)
admin.site.register(CheckPoint, CheckPointAdmin)
admin.site.register(CheckBlock, CheckBlockAdmin)
admin.site.register(CheckerUserSetting, CheckerUserSettingAdmin)
