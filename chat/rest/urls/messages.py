from django.urls import path

from chat.rest.views.messages import MessageList, MessageDetail

urlpatterns = [
    path("", MessageList.as_view(), name="chat-room-message-list"),
    path("/<uuid:message_uid>",MessageDetail.as_view(), name="chat-room-message-detail"),
]
