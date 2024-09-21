from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from chat.models import Message, ChatRoom
from chat.permissions import IsChatRoomMember
from chat.rest.serializers.messages import MessageSerializer


class MessageList(ListCreateAPIView):
    """Message list view"""

    permission_classes = [IsAuthenticated & IsChatRoomMember]
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_uid = self.kwargs.get("chat_room_uid")
        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        return (
            Message().get_active_instance().filter(chat_room=chat_room)
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


class MessageDetail(RetrieveUpdateDestroyAPIView):
    pass
