from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/mrna_coa_generator/', consumers.MyConsumer.as_asgi()),
]
