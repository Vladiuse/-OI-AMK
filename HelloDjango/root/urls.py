from django.urls import path
from . import views

appname = 'root'

urlpatterns = [
    path('', views.index, name='index'),
]