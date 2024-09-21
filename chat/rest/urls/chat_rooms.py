from django.urls import path, include

from chat.rest.views.chat_rooms import  ChatRoomList, ChatRoomDetail

urlpatterns = [
    path("", ChatRoomList.as_view(), name="user-chat-room-list"),
    path("/<uuid:chat_room_uid>", ChatRoomDetail.as_view(), name="chat-room-detail"),
    path("/<uuid:chat_room_uid>/messages",include("chat.rest.urls.messages")),
]
