"""
URL configuration for urosmart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myapp import views
from django.views.generic import TemplateView
urlpatterns = [
    path("admin/", admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('', views.home, name='home'),
    path('admin_index/', views.admin_index,name='index_admin'),
    path('nurse_index/', views.nurse_index,name='index_nurse'),
    path('privacy/', TemplateView.as_view(template_name="privacy.html"), name='privacy'),
    path('terms/', TemplateView.as_view(template_name="terms.html"), name='terms'),
    path('contact/', views.contact_us, name='contact_us'),
    path('users/',include('users.urls')),
    path('rooms/', include('rooms.urls')),
    path('devices/', include('devices.urls')),
    path('patients/',include('patients.urls')),
    path('history/',include('history.urls')),
    path('urine_monitor/',include('urine_monitor.urls'))
]

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
