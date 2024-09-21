from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from chat.rest.serializers.blocks import BlockListSerializer, BlockRoomMemberSerializer
from chat.models import BlockList


class BlockListFriend(ListCreateAPIView):
    """Blocked list friend for the user"""

    serializer_class = BlockListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockList().get_user_blocked_list(user=self.request.user)


class BlockRoomMember(ListCreateAPIView):
    """Blocked list room member for the user"""

    serializer_class = BlockRoomMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_uid = self.kwargs.get("room_uid")
        return BlockList.objects.filter(
            member_ship__chat_room__uid=room_uid
        ).select_related(
            "user",
            "blocked_by",
            "member_ship__user",
            "member_ship__chat_room__creator",
        )
