from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import NotFound

from chat.models import Message, ChatRoom
from chat.permissions import IsChatRoomActiveMember, HasWriteAccessToChatRoom
from chat.rest.serializers.messages import MessageSerializer

from shared.services import CachedQuerysetMixin
from shared.cache_key import get_chat_room_messages_cache_key


class MessageList(CachedQuerysetMixin, ListCreateAPIView):
    """Message list view"""

    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsChatRoomActiveMember()]
        return [HasWriteAccessToChatRoom()]

    def get_cache_key(self):
        room_uid = self.kwargs.get("chat_room_uid")
        return get_chat_room_messages_cache_key(room_uid)

    def fetch_queryset(self):
        room_uid = self.kwargs.get("chat_room_uid")

        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        messages = (
            Message()
            .get_active_instance()
            .filter(chat_room=chat_room)
            .select_related(
                "sender",
                "attachment",
                "reply_to__sender",
                "reply_to__attachment",
            )
            .prefetch_related(
                "read_by",
                "message_reactions__user",
            )
            .order_by("-created_at")
        )

        # Update the read_by field
        for message in messages:
            if self.request.user not in message.read_by.all():
                message.read_by.add(self.request.user)

        return messages

class MessageDetail(RetrieveUpdateDestroyAPIView):
    pass
