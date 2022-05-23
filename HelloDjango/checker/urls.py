from django.urls import path
from . import views
app_name = 'checker'

urlpatterns = [
    path('', views.index, name='index'),
    path('check_url/', views.check_url, name='check_url'),
    path('fix_ready_body/', views.check_url)
]