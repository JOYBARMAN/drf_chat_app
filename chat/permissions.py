from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated

from chat.models import ChatRoomMembership


class IsChatRoomActiveMember(IsAuthenticated):
    """Check if the user is active member of the chat room"""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        chat_room_uid = view.kwargs.get("chat_room_uid")
        return ChatRoomMembership.objects.filter(
            user=request.user, chat_room__uid=chat_room_uid, member_status="ACTIVE"
        ).exists()


class HasWriteAccessToChatRoom(IsAuthenticated):
    """Check if the user has write access to the chat room"""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        chat_room_uid = view.kwargs.get("chat_room_uid")
        member_ship = ChatRoomMembership.objects.filter(
            user=request.user, chat_room__uid=chat_room_uid, member_status="ACTIVE"
        ).first()

        if member_ship:
            if not member_ship.has_write_access:
                self.message = "You do not have write access to this chat room"
            return member_ship.has_write_access

        return False
