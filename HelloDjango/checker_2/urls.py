from django.urls import path
from . import views
app_name = 'checker_2'

urlpatterns = [
    path('', views.index, name='index'),
    path('check_url/', views.check_url, name='check_url'),
    path('analiz_land_text/', views.analiz_land_text),
    path('check_list', views.check_list),
]