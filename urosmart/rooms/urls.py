from django.urls import path,include
from rooms import views

urlpatterns = [
    #住出院
    # lp_current_list
    path('lp_current_list/', views.lp_current_list, name='lp_current_list'),
    path('lp_current_list/admit/<str:location>/', views.admit_patient, name='admit_patient'),
    path('lp_current_list/discharge/<str:location>/', views.discharge_patient, name='discharge_patient'),
    
    # lp_history_list
    path('lp_history_list/', views.lp_history_list, name='lp_history_list'),
    
    #病房管理
    path('roomconfig/', views.roomconfig_list, name='roomconfig_list'),
    path('roomconfig/add/', views.roomconfig_add, name='roomconfig_add'),
    path('roomconfig/edit/<int:room_id>/', views.roomconfig_edit, name='roomconfig_edit'),
    path('roomconfig/delete/<int:room_id>/', views.roomconfig_delete, name='roomconfig_delete'),
]