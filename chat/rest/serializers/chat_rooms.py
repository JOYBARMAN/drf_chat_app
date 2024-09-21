from rest_framework import serializers

from chat.models import ChatRoomMembership, ChatRoom, Message
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


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "uid",
            "content",
            "chat_room",
            "sender",
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


class ChatRoomMembershipListSerializer(ChatRoomMembershipSerializer):
    last_message_by = serializers.CharField()
    last_message_content = serializers.CharField()

    class Meta(ChatRoomMembershipSerializer.Meta):
        fields = ChatRoomMembershipSerializer.Meta.fields + [
            "last_message_by",
            "last_message_content",
        ]
        read_only_fields = fields
