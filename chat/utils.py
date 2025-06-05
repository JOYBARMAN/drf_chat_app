from django.db.models import (
    OuterRef,
    Subquery,
    Case,
    When,
    IntegerField,
    Value,
)
from django.core.paginator import Paginator, EmptyPage
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import AccessToken

from chat.models import ChatRoom, Message, ChatRoomMembership
from chat.choices import StatusChoices
from chat.rest.serializers.chat_rooms import ChatRoomMembershipListSerializer

from shared.decorator import cache_results, update_cache_results
from shared.cache_key import (
    get_user_chat_room_cache_key,
    get_chat_room_messages_cache_key,
    get_room_connected_users_cache_key,
)


User = get_user_model()


def get_or_create_private_chat(user1, user2):
    """Get or create a private chat room between two users."""

    room_name = generate_private_room_name(user1, user2)

    # Check if a room already exists with the same unique identifier
    # ChatRoom status will be active when user accepts the invitation
    room, created = ChatRoom.objects.get_or_create(
        name=room_name, status=StatusChoices.INACTIVE
    )

    return room


def generate_private_room_name(sender, receiver):
    """Generate a unique name for a private chat room between two users."""
    user_ids = sorted([sender.id, receiver.id])
    return f"private_chat_room_{user_ids[0]}_{user_ids[1]}"


def get_user_chat_room_group(user):
    """Get the group name for a user's chat rooms."""
    return f"user_{user.uid}_chat_rooms"


def validate_token(token):
    """Validate the token and return the user_id"""
    try:
        access_token = AccessToken(token)
        user_id = access_token.payload["user_id"]
        return user_id
    except Exception as e:
        return None


def get_token_from_scope(scope):
    """Extract the token from the scope."""

    headers = dict(scope.get("headers", {}))

    # Extract the authorizations header
    authorizations = headers.get(b"authorizations")

    if authorizations:
        # Decode the bytes to a string
        decoded_auth = authorizations.decode("utf-8")
        # Split the string and check if it contains at least two parts
        parts = decoded_auth.split(" ")
        if len(parts) == 2 and parts[0] == "Bearer":
            return parts[1]
    else:
        return None


@cache_results(lambda chat_room_uid: get_chat_room_messages_cache_key(chat_room_uid))
def chat_room_messages_query(chat_room_uid: str):
    """Get the messages for a chat room with related data."""
    return (
        Message()
        .get_active_instance()
        .filter(chat_room__uid=chat_room_uid)
        .select_related(
            "sender__profile",
            "attachment",
            "reply_to__sender__profile",
            "reply_to__attachment",
        )
        .prefetch_related(
            "read_by__profile",
            "message_reactions__user",
        )
        .order_by("-created_at")
    )


def update_message_cache(chat_room_uid: str):
    """Update the message cache for the chat room."""
    # Delete the cache
    cache_key = get_chat_room_messages_cache_key(chat_room_uid)
    cache.delete(cache_key)

    # Get the latest data
    return chat_room_messages_query(chat_room_uid)


def set_connected_user(room_name: str, sender):
    """Set connected user in cache"""
    room_connected_users = get_room_connected_users(room_name)
    room_connected_users.add(sender)
    cache.set(get_room_connected_users_cache_key(room_name), room_connected_users)


def get_room_connected_users(room_name: str):
    """Get connected users in a room"""
    connected_users = cache.get(get_room_connected_users_cache_key(room_name))
    if not connected_users:
        connected_users = set()
    return connected_users


def remove_connected_user(room_name: str, sender):
    """Remove connected user from the room"""
    room_connected_users = get_room_connected_users(room_name)
    if room_connected_users:
        room_connected_users.remove(sender)
    cache.set(get_room_connected_users_cache_key(room_name), room_connected_users)


@cache_results(lambda user: get_user_chat_room_cache_key(user.id))
def user_chat_room_query(user):
    """Get the chat room for the user with last message metadata."""

    messages = Message.objects.filter(chat_room=OuterRef("chat_room")).order_by(
        "-created_at"
    )

    return (
        ChatRoomMembership.objects.filter(user=user)
        .select_related(
            "user__profile",
            "oponent_user__profile",
            "chat_room__creator__profile",
        )
        .annotate(
            last_message_by=Subquery(messages.values("sender__username")[:1]),
            last_message_content=Subquery(messages.values("content")[:1]),
            last_message_created_at=Subquery(messages.values("created_at")[:1]),
            last_message_has_attachment=Subquery(messages.values("attachment")[:1]),
            has_last_message=Case(
                When(last_message_created_at__isnull=False, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .filter(has_last_message=1)
        .order_by("-last_message_created_at")
    )


def get_chat_room_serialized_data(user, page=1, page_size=20):
    """Get the chat room serialized data with pagination"""
    queryset = user_chat_room_query(user=user)
    paginator = Paginator(queryset, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    serialized_rooms = ChatRoomMembershipListSerializer(
        page_obj.object_list, many=True
    ).data

    return {
        "results": serialized_rooms,
        "pagination": {
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        },
    }
