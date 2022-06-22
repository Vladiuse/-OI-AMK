from django.urls import path
from . import views
app_name = 'manual'

urlpatterns = [
    path('', views.index, name='index'),
    path('note', views.note, name='note'),
    path('text_block', views.text_block, name='text_block'),
    path('list_point', views.list_point, name='list_point'),
    path('list_num', views.list_num, name='list_num'),
    path('picture', views.picture, name='picture'),
    path('slider', views.slider, name='slider'),
    path('slider_text', views.slider_text, name='slider_text'),
    # Заведение офферов 
    path('ss_offer', views.ss_offer, name='ss_offer'),
]