from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path(r'chats/<str:self_username>/<str:other_one_username>', consumers.Chats.as_asgi()),
]
