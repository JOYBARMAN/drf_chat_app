from django.core.cache import cache

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import NotFound

from chat.models import Message, ChatRoom
from chat.permissions import IsChatRoomActiveMember, HasWriteAccessToChatRoom
from chat.rest.serializers.messages import MessageSerializer
from chat.tasks import update_message_read_by

from shared.services import CachedQuerysetMixin
from shared.cache_key import get_chat_room_messages_cache_key


class MessageList(ListCreateAPIView):
    """Message list view"""

    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsChatRoomActiveMember()]
        return [HasWriteAccessToChatRoom()]

    def get_queryset(self):
        room_uid = self.kwargs.get("chat_room_uid")
        cache_key = get_chat_room_messages_cache_key(room_uid)

        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        messages = cache.get(cache_key)

        if messages is None:
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

            # Set the cache
            cache.set(cache_key, messages)

        # Update the read_by field for each message
        message_ids = list(messages.values_list("id", flat=True))
        if message_ids:
            update_message_read_by.delay(
                message_ids, user_id=self.request.user.id, room_uid=room_uid
            )

        return messages


class MessageDetail(RetrieveUpdateDestroyAPIView):
    pass
