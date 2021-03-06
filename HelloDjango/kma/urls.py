from django.urls import path
from . import views
app_name = 'kma'

urlpatterns = [
    path('default_webs/', views.default_webs, name='default_webs'),
    path('phones/', views.phones, name='phones'),
    path('get_phone_code/', views.get_phone_code),
    path('manual/', views.manual, name='manual'),
]