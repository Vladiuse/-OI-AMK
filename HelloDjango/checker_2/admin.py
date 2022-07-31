from django.contrib import admin
from .models import CheckPoint, Main, Sub
from ordered_model.admin import OrderedModelAdmin


class CheckPointAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'land_type', 'discount_type', 'for_geo', 'for_lang']


class MainAdmin(OrderedModelAdmin):
    list_display = ('name', 'move_up_down_links')


class SubAdmin(OrderedModelAdmin):
    list_display = ('name', 'move_up_down_links')
    list_filter = ['main__name']


admin.site.register(CheckPoint, CheckPointAdmin)
admin.site.register(Main, MainAdmin)
admin.site.register(Sub, SubAdmin)
