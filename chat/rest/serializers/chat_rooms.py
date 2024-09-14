from rest_framework import serializers

from chat.models import ChatRoomMembership, ChatRoom
from chat.rest.serializers.friends import UserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            "uid",
            "name",
            "group_name",
            "is_group_chat",
            "creator",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ChatRoomMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    chat_room = ChatRoomSerializer(read_only=True)

    class Meta:
        model = ChatRoomMembership
        fields = [
            "uid",
            "chat_room",
            "user",
            "role",
            "member_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
