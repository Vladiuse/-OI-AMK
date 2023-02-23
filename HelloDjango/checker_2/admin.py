from django.contrib import admin
from .models import CheckPoint, CheckBlock, CheckerUserSetting
from ordered_model.admin import OrderedModelAdmin



class CheckBlockAdmin(OrderedModelAdmin):

    list_display = ('id','name', 'move_up_down_links','manual_link', 'order', )
    list_display_links = ['id', 'name']

class CheckPointAdmin(OrderedModelAdmin):
    list_display = ['id', 'text', 'land_type', 'discount_type', 'for_geo', 'for_lang', 'move_up_down_links', 'is_notice','filter','manual_link','order']
    list_display_links = ['id', 'text']
    list_filter = ['parent__name']

class CheckerUserSettingAdmin(admin.ModelAdmin):
    list_display = ['user', 'left_bar', 'click_elem', 'other']
    list_display_links = ['user']


admin.site.register(CheckPoint, CheckPointAdmin)
admin.site.register(CheckBlock, CheckBlockAdmin)
admin.site.register(CheckerUserSetting, CheckerUserSettingAdmin)
