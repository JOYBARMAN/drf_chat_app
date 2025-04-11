from chat.utils import update_message_cache

from celery import shared_task
from channels.layers import get_channel_layer


@shared_task
def update_message_read_by(message_ids: list, user_id: int, room_uid: str):
    from django.contrib.auth import get_user_model
    from chat.models import Message

    # Fetch the user
    user = get_user_model().objects.get(id=user_id)

    # Fetch the user and messages
    messages = Message.objects.filter(id__in=message_ids).exclude(read_by=user)

    if messages:
        # Update the read_by field for each message
        for message in messages:
            message.read_by.add(user)

        # Update the cache
        update_message_cache(room_uid)

    return


@shared_task
def update_ws_chat_rooms(user_ids: list):
    from django.contrib.auth import get_user_model
    from chat.utils import update_user_ws_chat_rooms

    # Fetch the users
    users = get_user_model().objects.filter(id__in=user_ids)

    # Get the channel layer
    channel_layer = get_channel_layer()

    # Update the WebSocket chat rooms for the user
    for user in users:
        update_user_ws_chat_rooms(user=user, channel_layer=channel_layer)

    return
