from django.core.cache import cache

from rest_framework_simplejwt.tokens import AccessToken

from .models import ChatRoom, Message
from .choices import StatusChoices

from shared.cache_key import (
    get_chat_room_messages_cache_key,
    get_room_connected_users_cache_key,
)


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

    # Ensure that the users are not the same
    if sender == receiver:
        raise ValueError("Users must be different")

    # Generate a unique chat room
    user_ids = sorted([sender.id, receiver.id])
    return f"private_chat_room_{user_ids[0]}_{user_ids[1]}"


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


def update_message_cache(chat_room_uid: str):
    """Update the message cache for the chat room."""

    # Delete the cache
    cache_key = get_chat_room_messages_cache_key(chat_room_uid)
    cache.delete(cache_key)

    # Get the latest data
    latest_data = (
        Message()
        .get_active_instance()
        .filter(chat_room__uid=chat_room_uid)
        .select_related(
            "sender",
            "attachment",
            "reply_to__sender",
            "reply_to__attachment",
        )
        .prefetch_related(
            "read_by",
            "message_reactions__user",
        )
        .order_by("-created_at")
    )

    # Set new data in cache
    cache.set(cache_key, latest_data)

    return latest_data


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
