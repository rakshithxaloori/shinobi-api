from channels.routing import ProtocolTypeRouter, URLRouter


import chat.routing
from proeliumx.utils import TokenAuthMiddlewareStack

application = ProtocolTypeRouter(
    {
        "websocket": TokenAuthMiddlewareStack(
            URLRouter(chat.routing.websocket_urlpatterns)
        )
    }
)
