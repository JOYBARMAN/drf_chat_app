from django.urls import path

from chat.rest.views.friends import (
    AddFriendsView,
    FriendListView,
    FriendRequestListView,
    GroupChatRequestListView,
    SentRequestListView,
)

urlpatterns = [
    path("/add-friends", AddFriendsView.as_view(), name="add-friends"),
    path("/friends", FriendListView.as_view(), name="friend-list"),
    path("/friend-request", FriendRequestListView.as_view(), name="friend-request"),
    path("/sent-request", SentRequestListView.as_view(), name="sent-request"),
    path(
        "/group-chat-request",
        GroupChatRequestListView.as_view(),
        name="group-chat-request",
    ),
]
