from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/pluritest_form_generator/', consumers.MyConsumer.as_asgi()),
]
