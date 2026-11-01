import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aforro_market.settings')
django_asgi_app = get_asgi_application()   # must run BEFORE importing routing

from channels.routing import ProtocolTypeRouter, URLRouter
from stores.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})