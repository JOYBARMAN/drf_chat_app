from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from chat.choices import (
    ReactionChoices,
    UserRoleChoices,
    InvitationStatusChoices,
    MemberShipStatusChoices,
)

from shared.choices import StatusChoices
from shared.base_model import BaseModel
from shared.services import CacheMethod
from shared.cache_key import get_user_chat_room_cache_key


from versatileimagefield.fields import VersatileImageField

User = get_user_model()
ALLOWED_MEMBER_TO_SEND_INVITATION = ["ADMIN", "CO_ADMIN", "MODERATOR"]


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
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="creator_of_chat_rooms",
        help_text="User who created this chat room.",
    )

    def __str__(self):
        return self.name or self.group_name


class ChatRoomMembership(BaseModel):
    """Model to store membership of users in chat rooms."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_room_memberships",
        help_text="User who is a member of the chat room.",
    )
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text="Chat room in which the user is a member.",
    )
    role = models.CharField(
        max_length=20,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.MEMBER,
        help_text="Role of the user in the chat room.",
    )
    member_status = models.CharField(
        max_length=20,
        choices=MemberShipStatusChoices.choices,
        default=MemberShipStatusChoices.ACTIVE,
        help_text="Status of the member in the chat room.",
    )
    has_write_access = models.BooleanField(
        default=True,
        help_text="Indicates whether the user has write access in the chat room.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "chat_room"], name="unique_user_chat_room_membership"
            )
        ]

    def clean(self) -> None:
        super().clean()

        # Only 3 admins are allowed in a chat room
        if self.role == UserRoleChoices.ADMIN and self.chat_room.is_group_chat:
            # Count the current number of admins in the chat room excluding the current instance
            admin_count = (
                ChatRoomMembership.get_active_instance()
                .filter(chat_room=self.chat_room, role=UserRoleChoices.ADMIN)
                .distinct()
                .count()
            )
            # Check if adding this would exceed the admin limit
            if admin_count >= 3:
                raise ValidationError(
                    "A group chat room can have a maximum of 3 admins."
                )

        # Only 2 members are allowed in a private chat room
        if not self.chat_room.is_group_chat and not self.pk:
            user_count = (
                self.__class__.objects.filter(chat_room=self.chat_room)
                .distinct()
                .count()
            )
            if user_count >= 2:
                raise ValidationError(
                    "A private chat room can have a maximum of 2 members."
                )

    def save(self, *args, **kwargs):
        # Call clean to perform validations
        self.clean()

        # Remove cache for the user chat room list
        if self.pk:
            cache_key = get_user_chat_room_cache_key(user_id=self.user.id)
            CacheMethod().clear_cache(cache_key)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} in {self.chat_room}"


class ChatRoomInvitation(BaseModel):
    """Model to store chat room invitations."""

    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="invitations",
        help_text="Chat room for which the invitation is sent.",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_room_invitations",
        help_text="User who is invited to the chat room.",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_room_invitations_sent",
        help_text="User who sent the invitation to the chat room.",
    )
    invitation_status = models.CharField(
        max_length=20,
        choices=InvitationStatusChoices.choices,
        default=InvitationStatusChoices.PENDING,
        help_text="Status of the invitation.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chat_room", "receiver", "sender"],
                name="unique_chat_room_invitation",
            )
        ]

    def __str__(self):
        return f"{self.receiver.username} invited to {self.chat_room.name}"

    def clean(self):
        """Custom validation for the ChatRoomInvitation model."""
        super().clean()

        # Sender and receiver cannot be the same user
        if self.sender == self.receiver:
            raise ValidationError("Sender and receiver cannot be the same user.")

        # Only the creator/ of the chat room can send invitations
        if self.chat_room.is_group_chat and not self.send_request_access():
            raise ValidationError(
                "You do not have permission to send invitation for this chat room."
            )

    def send_request_access(self, sender=None, chat_room=None):
        # Check if the sender has the permission to send invitation for the group chat
        has_access = ChatRoomMembership.objects.filter(
            user=sender if sender else self.sender,
            chat_room=chat_room if chat_room else self.chat_room,
            role__in=ALLOWED_MEMBER_TO_SEND_INVITATION,
        ).exists()

        return has_access

    def save(self, *args, **kwargs):
        # Call clean to perform validations
        self.clean()

        # Update is_accepted field based on invitation status
        if self.invitation_status == InvitationStatusChoices.ACCEPTED and self.pk:
            # Add chat memebership if invitation is accepted
            for user in [self.sender, self.receiver]:
                ChatRoomMembership.objects.get_or_create(
                    user=user, chat_room=self.chat_room
                )
            # Update the chat room status for private chat
            if not self.chat_room.status == StatusChoices.ACTIVE:
                self.chat_room.status == StatusChoices.ACTIVE
                self.chat_room.save_dirty_fields()

        super().save(*args, **kwargs)

    def send_group_chat_invitation(self, chat_room, receiver, sender):
        """Send invitation to a user for a group chat room."""
        if chat_room.is_group_chat and not self.send_request_access(
            chat_room=chat_room, sender=sender
        ):
            return {"message": "You do not have permission to send invitation."}

        invitation, created = self.__class__.objects.get_or_create(
            chat_room=chat_room, receiver=receiver, sender=sender
        )

        if not created:
            return {"message": "Invitation already exists.", "invitation": invitation}

        return {"message": "Invitation sent successfully.", "invitation": invitation}

    def send_private_chat_invitation(self, receiver, sender):
        """Send invitation to a user for a private chat room."""
        from chat.utils import get_or_create_private_chat

        # Get or create a private chat room
        chat_room = get_or_create_private_chat(receiver, sender)

        invitation, created = self.__class__.objects.get_or_create(
            chat_room=chat_room, receiver=receiver, sender=sender
        )

        if not created:
            return {"message": "Invitation already exists.", "invitation": invitation}

        return {"message": "Invitation sent successfully.", "invitation": invitation}

    @classmethod
    def get_user_accepted_sent_invitation(self, user):
        """Get the list of accepted sent invitation of a user."""
        return self.objects.filter(
            sender=user,
            invitation_status=InvitationStatusChoices.ACCEPTED,
            chat_room__is_group_chat=False,
        ).select_related("receiver")

    @classmethod
    def get_user_accepted_received_invitation(self, user):
        """Get the list of accepted received invitation of a user."""
        return self.objects.filter(
            receiver=user,
            invitation_status=InvitationStatusChoices.ACCEPTED,
            chat_room__is_group_chat=False,
        ).select_related("sender")

    @classmethod
    def get_user_friend_list(self, user):
        """Get the list of friends of a user."""
        # Get the list of accepted sent and received invitations
        sent_invitations = self.get_user_accepted_sent_invitation(user)
        received_invitations = self.get_user_accepted_received_invitation(user)

        # Find the user who blocked the current user
        blocked_users = BlockList().get_user_blocked_by_list(user)

        # Collect friends from sent invitations and update the list with received invitations
        friends = set(invitation.receiver for invitation in sent_invitations)
        friends.update(invitation.sender for invitation in received_invitations)

        # Remove blocked users from the list
        friends.difference_update(User.objects.filter(id__in=blocked_users))

        return list(friends)

    @classmethod
    def get_user_add_friend_list(self, user):
        """Get the list of users who can be added as friends by a user."""

        # Get the list of accepted sent and received invitations
        sent_invitations = [
            ele.receiver.id for ele in self.get_user_accepted_sent_invitation(user)
        ]
        received_invitations = [
            ele.sender.id for ele in self.get_user_accepted_received_invitation(user)
        ]

        # Find the user who blocked the current user
        blocked_users = [ele for ele in BlockList().get_user_blocked_by_list(user)]
        # Arrange the exclude users list for current user
        exclude_users = set(
            sent_invitations + received_invitations + blocked_users + [user.id]
        )

        return User.objects.exclude(id__in=exclude_users)

    def get_user_friend_request(self, user):
        """Get the list of friend request of a user."""
        # Find invitations where the user is the receiver and the invitation is pending
        received_invitations = self.objects.filter(
            receiver=user,
            invitation_status=InvitationStatusChoices.PENDING,
            chat_room__is_group_chat=False,
        )
        return received_invitations

    def get_user_sent_request(self, user):
        """Get the list of sent request of a user."""
        # Find invitations where the user is the sender and the invitation is pending
        sent_invitations = self.objects.filter(
            sender=user,
            invitation_status=InvitationStatusChoices.PENDING,
            chat_room__is_group_chat=False,
        )
        return sent_invitations


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
        return f"Uid: {self.uid}"


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


class BlockList(BaseModel):
    """Model to store blocked users."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blocked_users",
        help_text="User who is blocked.",
    )
    member_ship = models.ForeignKey(
        ChatRoomMembership,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blocked_users",
        help_text="User who is blocked in the chat room.",
    )
    blocked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blocked_by_users",
        help_text="User who blocked the user.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "blocked_by"], name="unique_blocked_user"
            )
        ]

    def __str__(self):
        return f"{self.user} is blocked by {self.blocked_by}"

    def clean(self) -> None:
        super().clean()

        # Check if the user not try to block himself
        if self.user == self.blocked_by:
            raise ValidationError("You cannot block yourself.")

    def save(self, *args, **kwargs):
        # Call clean to perform validations
        self.clean()

        super().save(*args, **kwargs)

    @classmethod
    def get_user_blocked_list(self, user):
        """Get the list of blocked users by a user."""
        return self.objects.filter(
            blocked_by=user, member_ship__isnull=True
        ).select_related("user")

    @classmethod
    def get_user_blocked_by_list(self, user):
        """Get the list of user blocked by list"""
        return self.objects.filter(user=user, member_ship__isnull=True).values_list(
            "blocked_by", flat=True
        )
