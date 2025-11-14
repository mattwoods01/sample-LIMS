from django.urls import path 
from . import consumers

websocket_urlpatterns = [
    path('ws/lenti_cherrypick/', consumers.MyConsumer.as_asgi()),
]