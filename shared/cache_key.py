"""List of cache keys used in the application."""


def get_user_chat_room_cache_key(user_id):
    return f"user_chat_rooms_{user_id}"


def get_chat_room_messages_cache_key(chat_room_uid):
    return f"chat_room_messages_{chat_room_uid}"


def get_model_cache_key(model_name: str):
    return f"model_{model_name}"


def get_room_connected_users_cache_key(room_name: str):
    return f"connected_users_{room_name}"


def get_user_add_friends_cache_key(user_id):
    return f"user_add_friends_{user_id}"


def get_user_friend_request_cache_key(user_id):
    return f"friend_request_{user_id}"


def get_user_friend_list_cache_key(user_id):
    return f"friend_list_{user_id}"
