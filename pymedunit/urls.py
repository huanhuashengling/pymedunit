
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
    path('patient_info/<username>/', views.patient_info),
    re_path(r'^insert/', views.insert),
    re_path(r'^chart/', views.chart),
    re_path(r'^patient_list/', views.patient_list, name='patient_list'),
    path('item_chart/<username>/<item_id>', views.get_item_chart_data, name='get_item_chart_data'),
    path('items_chart/<username>/<indicator_id>', views.get_items_chart_data, name='get_items_chart_data'),
    # re_path(r'^get_investigate_project_data/$', views.get_investigate_project_data, name='get_investigate_project_data'),
    path('get_investigate_project_data/<plate_id>/', views.get_investigate_project_data, name='get_investigate_project_data'),
    path('get_investigate_indicator_data/<project_id>/', views.get_investigate_indicator_data, name='get_investigate_indicator_data'),
    path('get_investigate_item_data/<indicator_id>/', views.get_investigate_item_data, name='get_investigate_item_data'),
    
    re_path(r'sheet_upload/', views.sheet_upload, name='sheet_upload'),     #上传页面显示
    re_path(r'att_upload/', views.attachment_upload, name='att_upload'),    #处理上传请求
    # re_path(r'del_doc_file/', views.del_doc_file, name='del_doc_file'),     #单个删除
    # re_path(r'del_all_att/', views.del_all_att, name='del_all_att'),        #批量删除
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# 上传文件url路径
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
