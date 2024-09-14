from django.urls import path

from chat.rest.views.blocks import  BlockListFriend, BlockRoomMember

urlpatterns = [
    path("/by-me", BlockListFriend.as_view(), name="blocked-by-me-list"),
    path("/room-member/<uuid:room_uid>", BlockRoomMember.as_view(), name="blocked-room-member-list"),
]
