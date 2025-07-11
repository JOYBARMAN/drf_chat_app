from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import User, UserProfile

from chat.models import ChatRoomInvitation

from shared.notification_messages import INCOMING_FRIEND_REQUEST

from notifications.services import NotificationService


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "uid",
            "photo",
            "bio",
            "date_of_birth",
            "gender",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "uid",
            "username",
            "username",
            "first_name",
            "last_name",
            "email",
            "last_login",
            "created_at",
            "updated_at",
            "profile",
        ]
        read_only_fields = fields


class AddFriendSerializer(serializers.Serializer):
    """Serializer for adding friends"""

    friends_uid = serializers.UUIDField(write_only=True)
    message = serializers.CharField(max_length=255, read_only=True)

    def validate_friends_uid(self, value):
        """Validate the friends uid"""
        self.requested_friend = User.objects.filter(uid=value).first()
        self.user = self.context["request"].user

        # Check if the user exists
        if not self.requested_friend:
            raise serializers.ValidationError("User does not exist with this uid")
        # Check user is not try to request himself
        if self.requested_friend == self.user:
            raise serializers.ValidationError("You cannot add yourself as a friend")

        return value

    def create(self, validated_data):
        """Create a new friend request"""
        room_invitation = ChatRoomInvitation().send_private_chat_invitation(
            receiver=self.requested_friend,
            sender=self.user,
        )

        # Create a notification for the friend request
        from chat.rest.serializers.chat_rooms import ChatRoomInvitationSerializer

        notification = NotificationService(
            requested_user=self.user,
            message=INCOMING_FRIEND_REQUEST.format(fullname=self.user.fullname),
            instance=room_invitation["invitation"],
            method="POST",
            user_list=self.requested_friend,
            serializer=ChatRoomInvitationSerializer,
        )
        notification.create_notification()

        return room_invitation
