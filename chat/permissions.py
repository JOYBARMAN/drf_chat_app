from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated

from chat.models import ChatRoomMembership

class IsChatRoomMember(BasePermission):
    """Check if the user is a member of the chat room"""

    def has_permission(self, request, view):
        chat_room_uid = view.kwargs.get("chat_room_uid")
        return ChatRoomMembership.objects.filter(
            user=request.user, chat_room__uid=chat_room_uid
        ).exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)