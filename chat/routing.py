from django.urls import path

from chat.consumers import group_chat, private_chat

websocket_urlpatterns = [
    path("ws/ac/chat/<str:username>", private_chat.PrivateChatConsumer.as_asgi()),
    path("ws/ac/group-chat/<str:room_name>", group_chat.GroupChatConsumer.as_asgi()),
]