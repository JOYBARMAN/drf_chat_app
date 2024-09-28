from django.urls import path, include

from chat.rest.views.chat_rooms import  ChatRoomList, ChatRoomDetail, GroupChatList, GroupChatMember

urlpatterns = [
    path("", ChatRoomList.as_view(), name="user-chat-room-list"),
    path("/<uuid:chat_room_uid>", ChatRoomDetail.as_view(), name="chat-room-detail"),
    path("/group-chat", GroupChatList.as_view(), name="group-chat-list"),
    path("/group-chat/<uuid:chat_room_uid>/members", GroupChatMember.as_view(), name="group-chat-member-list"),
    path("/<uuid:chat_room_uid>/messages",include("chat.rest.urls.messages")),
]
