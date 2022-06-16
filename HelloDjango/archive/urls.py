from django.urls import path
from . import views
app_name = 'archive'

urlpatterns = [
    path('', views.index, name='index'),
    path('/add_site_category', views.add_site_category, name='add_site_category'),
    path('/get_sites_n_categorys', views.get_sites_n_categorys, name='get_sites_n_categorys'),
    path('/update_category', views.update_category, name='update_category'),
    path('/update_name_n_desc', views.update_name_n_desc), 
    path('/add_cataloge', views.add_cataloge),  
    path('/add_site_to_cataloge', views.add_site_to_cataloge),
    path('/remove_cataloge', views.remove_cataloge),
    path('/add_remote_site', views.add_remote_site)
    # path('/test', views.test),
]