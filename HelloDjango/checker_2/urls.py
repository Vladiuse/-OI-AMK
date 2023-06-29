from django.urls import path
from . import views
app_name = 'checker_2'

urlpatterns = [
    path('', views.index, name='index'),
    path('check_url/', views.check_url, name='check_url'),
    path('analiz_land_text/', views.analiz_land_text),
    path('change_status_of_user_checklist/', views.change_status_of_user_checklist),
    path('doc_page/', views.doc_page),
    path('dell_old/', views.dell_old, ),
    path('get-img-info/', views.image_info, name='get_img_info'),
    path('test/', views.test),
]