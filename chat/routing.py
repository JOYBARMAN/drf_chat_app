from django.urls import path

from .consumers import PrivateChatConsumer

websocket_urlpatterns = [
    path("ws/ac/chat/<str:username>", PrivateChatConsumer.as_asgi()),
]