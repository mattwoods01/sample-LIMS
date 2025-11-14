from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalogue/', views.database, name='database'),
    path('catalogue/filter', views.data_endpoint, name='data_endpoint')
]