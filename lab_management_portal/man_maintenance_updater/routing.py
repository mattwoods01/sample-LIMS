from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/man_maintenance_updater/', consumers.MyConsumer.as_asgi()),
]
