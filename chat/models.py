import uuid

from django.db import models
from django.contrib.auth import get_user_model

from .choices import StatusChoices, ReactionChoices

from dirtyfields import DirtyFieldsMixin
from versatileimagefield.fields import VersatileImageField

User = get_user_model()


class BaseModel(DirtyFieldsMixin, models.Model):
    """Base class for all other models."""

    uid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
        help_text="Unique identifier for this model instance.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp indicating when the instance was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp indicating when the instance was last updated.",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Status of the instance, typically used for soft deletion.",
    )

    def get_active_instance(self):
        """Get active instance of the model."""
        return self.__class__.objects.filter(status=StatusChoices.ACTIVE)

    class Meta:
        abstract = True


class ChatRoom(BaseModel):
    """Model to store chat rooms."""

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        help_text="Name of the chat room. Optional for private chats, recommended for group chats.",
    )
    group_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="Group name for the chat room, mainly used for identifying group chats.",
    )
    is_group_chat = models.BooleanField(
        default=False,
        help_text="Indicates whether the chat room is for group chat or private chat.",
    )

    members = models.ManyToManyField(
        User,
        related_name="chat_rooms",
        blank=True,
        help_text="Users who are members of this chat room.",
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="admin_of_chat_rooms",
        help_text="User who has administrative privileges for this chat room.",
    )

    def __str__(self):
        return self.name or self.group_name


class Attachment(BaseModel):
    """Model to store file attachments for messages."""

    attachment = models.FileField(
        upload_to="attachments/",
        null=True,
        blank=True,
        help_text="File attached to the message, can be any type of file.",
    )
    image = VersatileImageField(
        upload_to="images/",
        null=True,
        blank=True,
        help_text="Image file attached to the message.",
    )
    emoji_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Emoji or short description representing the attachment.",
    )

    def __str__(self):
        return self.attachment.name if self.attachment else "No Attachment"


class Message(BaseModel):
    """Model to store messages exchanged between users."""

    content = models.TextField(
        null=True,
        blank=True,
        help_text="Text content of the message. Can be empty if only an attachment is sent.",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text="User who sent the message.",
    )
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Chat room in which the message was sent.",
    )
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
        help_text="Attachment associated with the message, if any.",
    )
    read_by = models.ManyToManyField(
        User,
        related_name="read_messages",
        blank=True,
        help_text="Users who have read the message.",
    )
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
        help_text="The message to which this message is a reply, if any.",
    )

    def __str__(self):
        return self.content[:50] if self.content else "No Content"


class MessageReaction(BaseModel):
    """Model to store reactions to messages."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_reactions",
        help_text="User who reacted to the message.",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="message_reactions",
        help_text="Message that received the reaction.",
    )
    reaction_type = models.CharField(
        max_length=20,
        choices=ReactionChoices.choices,
        default=ReactionChoices.NONE,
        help_text="Type of reaction given by the user.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "message"], name="unique_user_message_reaction"
            )
        ]

    def __str__(self):
        return f"{self.user} reacted {self.reaction_type} on {self.message}"
