from django.contrib import admin
from .models import Site, SiteCategoty, Languege, Cataloge, Tag, Test
# Register your models here.

class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'path', 'description']
    list_display_links = ['name']

class LanguegeAdmin(admin.ModelAdmin):
    list_display = ['id', 'full', 'short', 'is_active']
    list_display_links = ['full','short']
    list_filter = ['is_active']

class CatalogeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']

class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'smile', 'html_class']
    list_display_links = ['text', 'smile', 'html_class']




admin.site.register(Site, SiteAdmin)
admin.site.register(SiteCategoty)
admin.site.register(Languege, LanguegeAdmin)
admin.site.register(Cataloge, CatalogeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Test)
