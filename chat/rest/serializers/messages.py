from rest_framework import serializers

from chat.models import Message, Attachment, MessageReaction, ChatRoom
from chat.choices import ReactionChoices
from chat.rest.serializers.friends import UserSerializer
from chat.utils import get_room_connected_users, set_connected_user


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
        read_only_fields = [
            "uid",
            "created_at",
            "updated_at",
        ]


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
    content = serializers.CharField(required=False, allow_blank=True)
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
            "is_edited",
            "sender",
            "attachment",
            "read_by",
            "reply_to",
            "message_reactions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uid",
            "is_edited",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        self.content = attrs.get("content", "").strip()
        self.attachment = attrs.get("attachment", {})
        self.attachment_value_exists = any(self.attachment.values())

        if not self.content and not self.attachment_value_exists:
            raise serializers.ValidationError(
                "You must provide either content or a valid attachment."
            )

        return attrs

    def create(self, validated_data):
        room_uid = self.context["view"].kwargs.get("chat_room_uid")
        user = self.context["request"].user

        # Check if the chat room exists
        try:
            chat_room = ChatRoom.objects.get(uid=room_uid)
        except ChatRoom.DoesNotExist:
            raise serializers.ValidationError("Chat room not found with the given uid")

        # Create attachment if provided
        if self.attachment_value_exists:
            self.attachment = Attachment.objects.create(**self.attachment)

        # Create message
        return Message.objects.create(
            content=self.content,
            chat_room=chat_room,
            sender=user,
            attachment=self.attachment if self.attachment_value_exists else None,
        )


class MessageDetailSerializer(MessageSerializer):
    """Serializer for message detail view, inheriting from MessageSerializer"""

    reaction = serializers.ChoiceField(
        choices=ReactionChoices.choices,
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )

    class Meta(MessageSerializer.Meta):
        fields = MessageSerializer.Meta.fields + [
            "status",
            "reaction",
        ]

    def validate(self, attrs):
        self.content = attrs.get("content", "").strip()
        self.attachment = attrs.get("attachment", {})
        self.attachment_value_exists = any(self.attachment.values())

        return attrs

    def update(self, instance, validated_data):
        user = self.context["request"].user
        reaction = validated_data.get("reaction", None)

        # Update the content and attachment if provided
        if self.content:
            instance.content = self.content

        # Check if the attachment exists then update or create it
        if self.attachment_value_exists:
            if instance.attachment:
                # Update fields on existing attachment
                attachment = instance.attachment
                for key, value in self.attachment.items():
                    setattr(attachment, key, value)
                attachment.save()

            else:
                instance.attachment = Attachment.objects.create(**self.attachment)

        if self.content or self.attachment_value_exists:
            # Mark the message as edited if content or attachment is updated
            instance.is_edited = True

        # Update the reaction if provided
        if reaction:
            # Check if the reaction already exists
            existance_reaction = MessageReaction.objects.filter(
                message=instance,
                user=user,
            ).first()
            # If a reaction exists, check if it needs to be updated or deleted
            # If the reaction type is different, update it; if it's the same, delete it
            if existance_reaction and existance_reaction.reaction_type != reaction:
                # Update existing reaction
                existance_reaction.reaction_type = reaction
                existance_reaction.save()
            elif existance_reaction:
                # Here the reaction is the same so remove it
                existance_reaction.delete()
            else:
                # Create a new reaction
                MessageReaction.objects.create(
                    message=instance,
                    user=user,
                    reaction_type=reaction,
                )

        # Update the status
        instance.status = validated_data.get("status", instance.status)

        instance.save()
        return instance
