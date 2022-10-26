"""
ASGI config for Stories project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Stories.settings')
#
# application = get_asgi_application()

import django
from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import EsayPayApp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyPay.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": AsgiHandler(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            EsayPayApp.routing.websocket_urlpatterns
        )
    ),
})
