from django.urls import path,include
from users import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('captcha/', include('captcha.urls')),

    #使用者帳戶資訊列表
    path('user_list/',views.user_list,name='user_list'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    ##使用者新增編輯刪除
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]