from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from chat.rest.serializers.friends import UserSerializer
from chat.models import ChatRoomInvitation


class AddFriendsView(ListAPIView):
    """Add friends list for the user"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoomInvitation().get_user_add_friend_list(user=self.request.user)


class FriendListView(ListAPIView):
    """Friend list for the user"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoomInvitation().get_user_friend_list(user=self.request.user)
