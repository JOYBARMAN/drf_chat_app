from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import NotFound

from chat.models import ChatRoom
from chat.permissions import IsChatRoomActiveMember, HasWriteAccessToChatRoom
from chat.rest.serializers.messages import MessageSerializer
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
    pass
