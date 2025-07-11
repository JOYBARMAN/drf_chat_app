from django.urls import path

from chat.consumers import group_chat, private_chat, chat_room

from notifications.routing import (
    websocket_urlpatterns as notification_websocket_urlpatterns,
)

websocket_urlpatterns = [
    path("ws/ac/chat/<str:username>", private_chat.PrivateChatConsumer.as_asgi()),
    path("ws/ac/group-chat/<str:room_name>", group_chat.GroupChatConsumer.as_asgi()),
    path(
        "ws/ac/me/chat-rooms",
        chat_room.UserChatRoomConsumer.as_asgi(),
    ),
] + notification_websocket_urlpatterns
