from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import DefaultWeb, Country, OfferPosition, UserApiKey, Language


class DefaultWebAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['iso', 'ru_full_name', 'phone', 'phone_code', 'currency', 'langs','iso3']
    list_display_links = ['iso', 'ru_full_name']
    search_fields = ['iso', 'ru_full_name']
    autocomplete_fields = ['language']

    list_filter = (
        ('phone', admin.EmptyFieldListFilter),
    )




class OfferPositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'pretty_name']
    list_display_links = ['pretty_name']

    @admin.display
    def pretty_name(self, obj):
        return obj.name.title()

class LanguageAdmin(admin.ModelAdmin):
    list_display = ['iso', 'russian_name']
    search_fields = ['russian_name', 'iso']

admin.site.register(DefaultWeb, DefaultWebAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(OfferPosition, OfferPositionAdmin)
admin.site.register(UserApiKey)
admin.site.register(Language, LanguageAdmin)

