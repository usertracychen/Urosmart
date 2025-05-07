from django.urls import path,include
from devices import views
 
urlpatterns = [
    path('sensor/data/', views.sensor_data_api),
    path("device_list/", views.device_list, name="device_list"),
    path("device/<str:chip_id>/", views.device_detail, name="device_detail"),
    path("device/delete/<str:chip_id>",views.device_delete,name="device_delete"),
    path('register_device/', views.register_device, name='register_device'),
    
]