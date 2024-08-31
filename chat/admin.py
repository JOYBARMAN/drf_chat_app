from django.contrib import admin

from .models import ChatRoom, Attachment, Message, MessageReaction


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "group_name",
        "is_group_chat",
        "admin",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_group_chat", "admin", "created_at", "updated_at")
    search_fields = ("name", "group_name", "admin__username")
    readonly_fields = ("uid", "created_at", "updated_at")
    filter_horizontal = (
        "members",
    )  # If many-to-many relationships should use filter_horizontal


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("attachment", "emoji_description", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("attachment", "emoji_description")
    readonly_fields = ("uid", "created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("content", "sender", "chat_room", "created_at", "updated_at")
    list_filter = ("sender", "chat_room", "created_at", "updated_at")
    search_fields = (
        "content",
        "sender__username",
        "chat_room__name",
        "chat_room__group_name",
    )
    readonly_fields = ("uid", "created_at", "updated_at")
    raw_id_fields = (
        "reply_to",
        "attachment",
    )  # Improves performance for large datasets
    filter_horizontal = (
        "read_by",
    )  # If many-to-many relationships should use filter_horizontal


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "reaction_type", "created_at", "updated_at")
    list_filter = ("reaction_type", "created_at", "updated_at")
    search_fields = ("user__username", "message__content", "reaction_type")
    readonly_fields = ("uid", "created_at", "updated_at")
