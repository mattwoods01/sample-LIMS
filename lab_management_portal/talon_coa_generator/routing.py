from django.urls import path 
from . import consumers

websocket_urlpatterns = [
    path('ws/talon_coa_generator/', consumers.MyConsumer.as_asgi()),
]