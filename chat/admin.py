from django.contrib import admin

from .models import (
    ChatRoom,
    ChatRoomMembership,
    ChatRoomInvitation,
    Attachment,
    Message,
    MessageReaction,
    BlockList,
)


class BaseModelAdmin(admin.ModelAdmin):
    """Base Model Admin with common fields from BaseModel."""

    readonly_fields = [
        "uid",
        "created_at",
        "updated_at",
        "status",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + [
                "uid",
            ]
        return self.readonly_fields

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if "uid" not in list_display:
            return [
                "uid",
            ] + list_display
        return list_display


class ChatRoomMembershipInline(admin.TabularInline):
    model = ChatRoomMembership
    extra = 1
    fields = [
        "user",
        "role",
    ]
    # readonly_fields = [
    #     "user",
    #     "role",
    # ]


class ChatRoomInvitationInline(admin.TabularInline):
    model = ChatRoomInvitation
    extra = 1
    fields = ["chat_room","receiver", "sender", "invitation_status"]
    # readonly_fields = ["receiver", "sender", "is_accepted", "invitation_status"]


@admin.register(ChatRoom)
class ChatRoomAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "name",
        "group_name",
        "is_group_chat",
        "creator",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "name",
        "group_name",
    ]
    inlines = [ChatRoomMembershipInline, ChatRoomInvitationInline]
    list_filter = [
        "is_group_chat",
        "status",
    ]


@admin.register(ChatRoomMembership)
class ChatRoomMembershipAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "user",
        "chat_room",
        "role",
        "member_status",
        "has_write_access",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "user__username",
        "chat_room__name",
    ]
    list_filter = [
        "role",
        "chat_room",
        "status",
        "member_status",
    ]


@admin.register(ChatRoomInvitation)
class ChatRoomInvitationAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "chat_room",
        "receiver",
        "sender",
        "invitation_status",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "chat_room__name",
        "receiver__username",
        "sender__username",
    ]
    list_filter = [
        "invitation_status",
        "status",
    ]
    # readonly_fields = [
    #     "chat_room",
    #     "receiver",
    #     "sender",
    #     "uid",
    #     "created_at",
    #     "updated_at",
    #     "status",
    # ]


@admin.register(Attachment)
class AttachmentAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "attachment",
        "image",
        "emoji_description",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "emoji_description",
    ]
    list_filter = [
        "emoji_description",
        "status",
    ]


@admin.register(Message)
class MessageAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "content",
        "sender",
        "chat_room",
        "attachment",
        "reply_to",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "content",
        "sender__username",
        "chat_room__name",
    ]
    list_filter = [
        "chat_room",
        "reply_to",
        "status",
    ]
    # readonly_fields = [
    #     "read_by",
    #     "uid",
    #     "created_at",
    #     "updated_at",
    #     "status",
    # ]


@admin.register(MessageReaction)
class MessageReactionAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "user",
        "message",
        "reaction_type",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "user__username",
        "message__content",
    ]
    list_filter = [
        "reaction_type",
        "status",
    ]
    # readonly_fields = [
    #     "user",
    #     "message",
    #     "uid",
    #     "created_at",
    #     "updated_at",
    #     "status",
    # ]

@admin.register(BlockList)
class BlockListAdmin(BaseModelAdmin):
    list_display = [
        "uid",
        "user",
        "member_ship",
        "blocked_by",
        "created_at",
        "updated_at",
        "status",
    ]
    search_fields = [
        "uid",
        "user__username",
        "blocked_by__username",
    ]
    list_filter = [
        "status",
    ]
    # readonly_fields = [
    #     "user",
    #     "blocked_by",
    #     "uid",
    #     "created_at",
    #     "updated_at",
    #     "status",
    # ]