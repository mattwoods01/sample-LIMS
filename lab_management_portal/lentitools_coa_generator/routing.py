from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/lentitools_coa_generator/', consumers.MyConsumer.as_asgi()),
]
