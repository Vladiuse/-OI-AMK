from django.contrib import admin
from .models import DefaultWeb, PhoneNumber
# Register your models here.


class DefaultWebAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['id','short','ru_full_name', 'phone',  'phone_code']
    list_display_links = ['short', 'phone', 'ru_full_name']


admin.site.register(DefaultWeb, DefaultWebAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
