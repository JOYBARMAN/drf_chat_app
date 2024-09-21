from rest_framework import serializers

from chat.models import Message, Attachment, MessageReaction, ChatRoom
from chat.rest.serializers.friends import UserSerializer


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "uid",
            "attachment",
            "image",
            "emoji_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uid", "created_at", "updated_at"]


class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = [
            "uid",
            "user",
            "reaction_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class MessageReplySerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachment = AttachmentSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "uid",
            "content",
            "sender",
            "attachment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False)
    sender = UserSerializer(read_only=True)
    read_by = UserSerializer(read_only=True, many=True)
    attachment = AttachmentSerializer(required=False)
    reply_to = MessageReplySerializer(read_only=True)
    message_reactions = MessageReactionSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = [
            "uid",
            "content",
            "sender",
            "attachment",
            "read_by",
            "reply_to",
            "message_reactions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields.copy()
        read_only_fields.remove("content")
        read_only_fields.remove("attachment")

    def validate(self, attrs):
        content = attrs.get("content")
        attachment = attrs.get("attachment")
        attachment_value_exists = any(attachment.values())

        if not content and not attachment_value_exists:
            raise serializers.ValidationError(
                "You must provide either content or attachment"
            )

        return attrs

    def create(self, validated_data):
        room_uid = self.context["view"].kwargs.get("chat_room_uid")
        user = self.context["request"].user
        content = validated_data.get("content")
        attachment = validated_data.get("attachment")

        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise serializers.ValidationError("Chat room not found with the given uid")

        # Create attachment if provided
        if attachment:
            attachment = Attachment.objects.create(**attachment)

        # Create message
        message = Message.objects.create(
            chat_room=chat_room,
            sender=user,
            content=content if content else None,
            attachment=attachment if attachment else None,
        )
        message.read_by.add(user)

        return message
