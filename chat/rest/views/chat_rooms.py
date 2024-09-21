from django.db.models import OuterRef, Subquery

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from chat.models import ChatRoomMembership, Message
from chat.rest.serializers.chat_rooms import (
    ChatRoomMembershipListSerializer,
)


class ChatRoomList(ListAPIView):
    """Chat room list for the user"""

    serializer_class = ChatRoomMembershipListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Subquery to get the last message username and contentin each chat room
        last_message_username_subquery = (
            Message.objects.filter(chat_room=OuterRef("chat_room"))
            .order_by("-created_at")
            .values("sender__username")[:1]
        )
        last_message_content_subquery = (
            Message.objects.filter(chat_room=OuterRef("chat_room"))
            .order_by("-created_at")
            .values("content")[:1]
        )

        return (
            ChatRoomMembership.objects.filter(user=self.request.user)
            .select_related(
                "user",
                "chat_room__creator",
            )
            .annotate(
                last_message_by=Subquery(last_message_username_subquery),
                last_message_content=Subquery(last_message_content_subquery),
            )
        )


class ChatRoomDetail(RetrieveAPIView):
    """Chat room detail view"""
    pass
