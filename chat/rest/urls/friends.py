from django.urls import path

from chat.rest.views.friends import AddFriendsView, FriendListView

urlpatterns = [
    path("/add-friends", AddFriendsView.as_view(), name="add-friends"),
    path("/friend-list", FriendListView.as_view(), name="friend-list"),
]
