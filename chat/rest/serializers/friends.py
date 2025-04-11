from django.contrib.auth import get_user_model

from rest_framework import serializers

from chat.models import ChatRoomInvitation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = fields


class AddFriendSerializer(serializers.Serializer):
    """Serializer for adding friends"""

    friends_uid = serializers.UUIDField(write_only=True)
    message = serializers.CharField(max_length=255, read_only=True)

    def validate_friends_uid(self, value):
        """Validate the friends uid"""
        self.requested_friend = User.objects.filter(uid=value).first()
        if not self.requested_friend:
            raise serializers.ValidationError("User does not exist with this uid")

        return value

    def create(self, validated_data):
        """Create a new friend request"""
        return ChatRoomInvitation().send_private_chat_invitation(
            receiver=self.requested_friend,
            sender=self.context["request"].user,
        )
