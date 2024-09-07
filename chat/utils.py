from rest_framework_simplejwt.tokens import AccessToken

from .models import ChatRoom
from .choices import StatusChoices


def get_or_create_private_chat(user1, user2):
    """Get or create a private chat room between two users."""

    room_name = generate_private_room_name(user1, user2)

    # Check if a room already exists with the same unique identifier
    #ChatRoom status will be active when user accepts the invitation
    room, created = ChatRoom.objects.get_or_create(name=room_name, status=StatusChoices.INACTIVE)

    return room


def generate_private_room_name(sender, receiver):
    """Generate a unique name for a private chat room between two users."""

    # Ensure that the users are not the same
    if sender == receiver:
        raise ValueError("Users must be different")

    # Generate a unique chat room
    user_ids = sorted([sender.id, receiver.id])
    return f"private_room_{user_ids[0]}_{user_ids[1]}"


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
