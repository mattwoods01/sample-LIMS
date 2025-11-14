from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import man_maintenance_updater.routing
import scan_maintenance_updater.routing
import pluritest_form_generator.routing
import mrna_coa_generator.routing
import lentitools_coa_generator.routing
import attachment_uploader.routing
import talon_coa_generator.routing
import lentipool_analysis_tool.routing
import lenti_cherrypick.routing

application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        "websocket": AuthMiddlewareStack(
            URLRouter(scan_maintenance_updater.routing.websocket_urlpatterns) + 
            URLRouter(man_maintenance_updater.routing.websocket_urlpatterns) + 
            URLRouter(pluritest_form_generator.routing.websocket_urlpatterns) +
            URLRouter(mrna_coa_generator.routing.websocket_urlpatterns) +
            URLRouter(lentitools_coa_generator.routing.websocket_urlpatterns) +
            URLRouter(attachment_uploader.routing.websocket_urlpatterns) + 
            URLRouter(talon_coa_generator.routing.websocket_urlpatterns) +
            URLRouter(lentipool_analysis_tool.routing.websocket_urlpatterns) +
            URLRouter(lenti_cherrypick.routing.websocket_urlpatterns)
        ),
    }
)

