from django.contrib import admin
from .models import DefaultWeb, Country, OfferPosition, UserApiKey, Language


class DefaultWebAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['iso', 'ru_full_name', 'phone', 'phone_code', 'currency', 'langs',]
    list_display_links = ['iso', 'phone', 'ru_full_name']
    autocomplete_fields = ['language']


class OfferPositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']

class LanguageAdmin(admin.ModelAdmin):
    list_display = ['iso', 'russian_name']
    search_fields = ['russian_name', 'iso']

admin.site.register(DefaultWeb, DefaultWebAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(OfferPosition, OfferPositionAdmin)
admin.site.register(UserApiKey)
admin.site.register(Language, LanguageAdmin)

