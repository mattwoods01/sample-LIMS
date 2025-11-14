"""
URL configuration for lab_management_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import include, path

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("Home/", include('Home.urls')),
    path("man_maintenance_updater/", include('man_maintenance_updater.urls')),
    path("scan_maintenance_updater/", include('scan_maintenance_updater.urls')),
    path("lentitools_coa_generator/", include('lentitools_coa_generator.urls')),
    path("mrna_coa_generator/", include('mrna_coa_generator.urls')),
    path("talon_coa_generator/", include('talon_coa_generator.urls')),
    path("pluritest_form_generator/", include('pluritest_form_generator.urls')),
    path("attachment_uploader/", include('attachment_uploader.urls')),
    path("lentipool_analysis_tool/", include('lentipool_analysis_tool.urls')),
    path("lenti_cherrypick/", include('lenti_cherrypick.urls')),
]
