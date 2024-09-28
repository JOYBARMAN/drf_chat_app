from django.db.models import OuterRef, Subquery

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from chat.models import ChatRoomMembership, Message, ChatRoom
from chat.rest.serializers.chat_rooms import (
    ChatRoomMembershipListSerializer,
    ChatRoomSerializer,
    ChatRoomMembershipSerializer,
    GroupChatMemberInviteSerializer,
)
from chat.permissions import IsChatRoomActiveMember, IsMemberHasInvitationAccess, HasUpdateAccessToRoomMembership


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


class GroupChatList(ListCreateAPIView):
    """Group chat create view"""

    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        member_ship = ChatRoomMembership.objects.filter(
            user=self.request.user, chat_room__is_group_chat=True
        ).select_related("chat_room__creator")

        return [membership.chat_room for membership in member_ship]


class GroupChatDetail(RetrieveAPIView):
    """Group chat detail view"""

    pass


class GroupChatMember(ListCreateAPIView):
    """Group chat members list view"""

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ChatRoomMembershipSerializer
        return GroupChatMemberInviteSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsChatRoomActiveMember()]
        return [IsMemberHasInvitationAccess()]

    def get_queryset(self):
        try:
            chat_room = ChatRoom.objects.get(uid=self.kwargs.get("chat_room_uid"))
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        if not chat_room.is_group_chat:
            raise NotFound("Chat room is not a group chat")

        return ChatRoomMembership.objects.filter(chat_room=chat_room).select_related(
            "user", "chat_room__creator"
        )


class GroupChatMemberDetail(RetrieveUpdateAPIView):
    """Group chat member detail view"""

    serializer_class = ChatRoomMembershipSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsChatRoomActiveMember()]
        return [HasUpdateAccessToRoomMembership()]
        # return [IsAuthenticated()]

    def get_object(self):
        try:
            chat_room = ChatRoom.objects.get(uid=self.kwargs.get("chat_room_uid"))
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found with the given uid")

        if not chat_room.is_group_chat:
            raise NotFound("Chat room is not a group chat")

        try:
            return ChatRoomMembership.objects.get(
                uid=self.kwargs.get("member_ship_uid")
            )
        except ChatRoomMembership.DoesNotExist:
            raise NotFound("Chat room member not found with the given uid")
