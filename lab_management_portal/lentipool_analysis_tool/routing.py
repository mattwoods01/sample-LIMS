from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/lentipool_analysis_tool/', consumers.MyConsumer.as_asgi()),
]
