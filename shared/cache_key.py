def get_user_chat_room_cache_key(user_id):
    return f"user_chat_rooms_{user_id}"


def get_chat_room_messages_cache_key(chat_room_uid):
    return f"chat_room_messages_{chat_room_uid}"
