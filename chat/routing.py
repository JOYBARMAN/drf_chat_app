from django.urls import path

from chat.consumers import private_chat,room_chat

websocket_urlpatterns = [
    path("ws/ac/chat/<str:username>", private_chat.PrivateChatConsumer.as_asgi()),
    path("ws/ac/chat/room/<str:room_name>", room_chat.RoomChatConsumer.as_asgi()),
]