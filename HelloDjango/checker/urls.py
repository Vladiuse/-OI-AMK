from django.urls import path
from . import views
app_name = 'checker'

urlpatterns = [
    path('', views.index, name='index'),
    path('check_url/', views.check_url, name='check_url'),
    path('analiz_land_text/', views.analiz_land_text),
    path('check_url_no_js/', views.check_url_no_js, name='check_url_no_js'),
    path('get_kma_rekl/', views.get_kma_rekl, name='get_kma_rekl'),
    path('check_iframe/', views.check_iframe, name='check_iframe'),
    path('iframe/', views.iframe, name='iframe'),
]