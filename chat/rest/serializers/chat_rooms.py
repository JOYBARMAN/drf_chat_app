from django.contrib.auth import get_user_model

from rest_framework import serializers

from chat.models import ChatRoomMembership, ChatRoom, Message, ChatRoomInvitation
from chat.rest.serializers.friends import UserSerializer
from chat.choices import UserRoleChoices

User = get_user_model()


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
        read_only_fields = [
            "uid",
            "created_at",
            "updated_at",
            "group_name",
            "creator",
            "is_group_chat",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        validated_data["is_group_chat"] = True

        # Create the chat room
        chat_room = super().create(validated_data)

        # Create the membership for the creator
        member_ship, created = ChatRoomMembership.objects.get_or_create(
            chat_room=chat_room, user=user, role=UserRoleChoices.ADMIN
        )

        return chat_room


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


class GroupChatMemberInviteSerializer(serializers.Serializer):
    users = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        many=True,
        slug_field="email",
        required=True,
        write_only=True,
    )
    message = serializers.CharField(required=False, read_only=True)

    def create(self, validated_data):
        chat_room_uid = self.context["view"].kwargs.get("chat_room_uid")
        sender = self.context["request"].user

        try:
            chat_room = ChatRoom.objects.get(uid=chat_room_uid)
        except ChatRoom.DoesNotExist:
            raise serializers.ValidationError("Chat room not found with the given uid")

        if not chat_room.is_group_chat:
            raise serializers.ValidationError("Chat room is not a group chat")

        for user in validated_data["users"]:
            try:
                ChatRoomInvitation().send_group_chat_invitation(
                    chat_room=chat_room, sender=sender, receiver=user
                )
            except Exception as e:
                error_message = str(e).strip("[]'")
                raise serializers.ValidationError({"detail":error_message})

        validated_data["message"] = "Invitation sent successfully"
        return validated_data
