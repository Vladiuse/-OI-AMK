from django.contrib import admin
from .models import DefaultWeb, PhoneNumber, OfferPosition, UserApiKey


class DefaultWebAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['id', 'short', 'ru_full_name', 'phone', 'phone_code', 'currency', 'langs']
    list_display_links = ['short', 'phone', 'ru_full_name']


class OfferPositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']


admin.site.register(DefaultWeb, DefaultWebAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
admin.site.register(OfferPosition, OfferPositionAdmin)
admin.site.register(UserApiKey)

