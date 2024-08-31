from .models import ChatRoom


def get_or_create_private_chat(user1, user2):
    """Get or create a private chat room between two users."""

    room_name = generate_private_room_name(user1, user2)

    # Check if a room already exists with the same unique identifier
    room, created = ChatRoom.objects.get_or_create(name=room_name, is_group_chat=False)

    # If the room was just created, add the members
    if created:
        room.members.add(user1, user2)

    return room


def generate_private_room_name(user1, user2):
    """Generate a unique name for a private chat room between two users."""

    # Ensure that the users are not the same
    if user1 == user2:
        raise ValueError("Users must be different")

    # Generate a unique chat room
    user_ids = sorted([user1.id, user2.id])
    return f"private_{user_ids[0]}_{user_ids[1]}"
