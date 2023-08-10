from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


app_name = 'checker_2'

router = DefaultRouter()
router.register(r'domains', views.DomainViewSet)

site_images_list = views.SiteImageViewSet.as_view({
    'get': 'list',
    'post': 'create_or_update'
})

site_images_detail = views.SiteImageViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

site_image_load = views.SiteImageViewSet.as_view({
    'get': 'load_orig'
})
make_thumb = views.SiteImageViewSet.as_view({
    'get': 'make_thumb'
})

load_make_thumb = views.SiteImageViewSet.as_view({
    'get': 'load_make_thumb'
})

urlpatterns = [
    path('', views.index, name='index'),
    path('check_url/', views.check_url, name='check_url'),
    path('analiz_land_text/', views.analiz_land_text),
    path('change_status_of_user_checklist/', views.change_status_of_user_checklist),
    path('doc_page/', views.doc_page),
    path('dell_old/', views.dell_old, ),
    path('get-img-info/', views.image_info, name='get_img_info'),
    path('test/', views.test),


    # path('checker_2/get-img-info/', views.image_info),
    path('domains/<int:domain_id>/site-images/', site_images_list, name='image-list'),
    path('site-images/<int:image_id>/', site_images_detail, name='image-detail'),
    path('site-images/<int:image_id>/load-orig/', site_image_load, name='image-load-orig'),
    path('site-images/<int:image_id>/make-thumb/', make_thumb, name='image-make-thumb'),
    path('site-images/<int:image_id>/load-make-thumb/', load_make_thumb, name='load-make-thumb'),
    path('', include(router.urls)),
    path('tasks/<int:task_id>/', views.crop_task, name='crop_task'),
    path('test_api/<int:domain_id>/', views.crop_images, name='create_crop_images'),
]