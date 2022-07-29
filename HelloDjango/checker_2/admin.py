from django.contrib import admin
from .models import CheckPoint


class CheckPointAdmin(admin.ModelAdmin):
    list_display = ['id', 'text','land_type', 'discount_type', 'for_geo', 'for_lang']


admin.site.register(CheckPoint, CheckPointAdmin)
