from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import NotFound

from chat.models import ChatRoom, Message
from chat.permissions import (
    IsChatRoomActiveMember,
    HasWriteAccessToChatRoom,
    IsOwnMessage,
)
from chat.rest.serializers.messages import MessageSerializer,MessageDetailSerializer
from chat.tasks import update_message_read_by
from chat.utils import chat_room_messages_query


class MessageList(ListCreateAPIView):
    """Message list view"""

    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsChatRoomActiveMember()]
        return [HasWriteAccessToChatRoom()]

    def get_queryset(self):
        room_uid = self.kwargs.get("chat_room_uid")

        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        messages = chat_room_messages_query(chat_room.uid)

        # Update the read_by field for each message
        message_ids = list(messages.values_list("id", flat=True))
        if message_ids:
            update_message_read_by.delay(
                message_ids,
                user_id=self.request.user.id,
                room_uid=room_uid,
                room_name=chat_room.name,
            )

        return messages


class MessageDetail(RetrieveUpdateDestroyAPIView):
    """Message detail view"""

    serializer_class = MessageDetailSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsChatRoomActiveMember()]
        return [IsOwnMessage()]

    def get_object(self):
        room_uid = self.kwargs.get("chat_room_uid")
        message_uid = self.kwargs.get("message_uid")

        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        messages = chat_room_messages_query(chat_room.uid)

        # Check if the message exists in the chat room
        try:
            return messages.get(uid=message_uid)
        except Message.DoesNotExist:
            raise NotFound("Message not found with the given uid in this chat room")
