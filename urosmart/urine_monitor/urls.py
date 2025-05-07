from django.urls import path
from urine_monitor import views

urlpatterns = [
    #顯示尿量
    # weight_display
    path('weight_display/', views.weight_display, name='weight_display'),
    path('weight_display_dashboard/',views.weight_display_dashboard,name='weight_display_dashboard'),
    path("dashboard/api/", views.weight_display_dashboard_api,name="weight_display_dashboard_api"),
    path('weight_display_dashboard/<str:room_number>/<str:patient_id>/',views.room_detail,name="room_detail"),
    # 提交勾選後 -> nurse
    path('weight_display/submit/', views.weight_display_submit, name='weight_display_submit'),
    path('weight_display_nurse/', views.weight_display_nurse, name='weight_display_nurse'),
    path('weight_display_nurse/delete/<str:chip_id>/', views.weight_display_nurse_delete, name='weight_display_nurse_delete'),
    path("nurse/api/", views.weight_display_nurse_api, name="weight_display_nurse_api"),

]