from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/attachment_uploader/', consumers.MyConsumer.as_asgi()),
]
