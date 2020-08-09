
"""pymedunit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path('patient_info/<username>/', views.patient_info),
    re_path(r'^time/$', views.current_datetime),
    re_path(r'^time/plus/(\d{1,2})/$', views.hours_ahead),
    re_path(r'^insert/', views.insert),
    re_path(r'^chart/', views.chart),
    re_path(r'^patient_list/', views.patient_list),
    re_path(r'^api/data/$', views.get_data, name='api-data'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
