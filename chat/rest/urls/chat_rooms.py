from django.urls import path

from chat.rest.views.chat_rooms import  ChatRoomList

urlpatterns = [
    path("", ChatRoomList.as_view(), name="user-chat-room-list"),
]
