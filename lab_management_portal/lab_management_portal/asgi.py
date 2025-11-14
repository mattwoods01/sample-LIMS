"""
ASGI config for lab_management_portal project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import man_maintenance_updater.routing
import mrna_coa_generator.routing
import scan_maintenance_updater.routing
import lentitools_coa_generator.routing
import pluritest_form_generator.routing
import mrna_coa_generator.routing
import attachment_uploader.routing
import talon_coa_generator.routing
import lentipool_analysis_tool.routing
import lenti_cherrypick.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_management_portal.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            man_maintenance_updater.routing.websocket_urlpatterns +
            scan_maintenance_updater.routing.websocket_urlpatterns +
            lentitools_coa_generator.routing.websocket_urlpatterns + 
            pluritest_form_generator.routing.websocket_urlpatterns + 
            mrna_coa_generator.routing.websocket_urlpatterns + 
            attachment_uploader.routing.websocket_urlpatterns + 
            talon_coa_generator.routing.websocket_urlpatterns +
            lentipool_analysis_tool.routing.websocket_urlpatterns +
            lenti_cherrypick.routing.websocket_urlpatterns
        )
    ),
})

