from django.urls import path,include
from history import views

urlpatterns = [
    # show_history
    path('show_history/', views.show_history, name='show_history'),
    path('show_history/daily',views.show_daily_urine_volumes,name="show_history_daily"),
]