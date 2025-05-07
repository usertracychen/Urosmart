from django.urls import path,include
from patients import views

urlpatterns = [
    path('caregiver/login/', views.caregiver_login, name='caregiver_login'),
    path('caregiver_index/', views.caregiver_index,name='index_caregiver'),
]