from django.contrib.auth import get_user_model

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.utils import update_message_cache, get_user_chat_room_group

# Get the channel layer
channel_layer = get_channel_layer()
# User model
User = get_user_model()


@shared_task
def update_message_read_by(
    message_ids: list, user_id: int, room_uid: str, room_name: str
):
    from chat.models import Message

    # Fetch the user
    user = User.objects.filter(id=user_id).first()

    # Fetch the user and messages
    messages = Message.objects.filter(id__in=message_ids).exclude(read_by=user)

    if messages:
        # Update the read_by field for each message
        for message in messages:
            message.read_by.add(user)

        # Update the cache
        update_message_cache(room_uid)
        # Send message to the WebSocket group
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "chat_message",
            },
        )

    return


@shared_task
def update_ws_chat_rooms(user_ids: list):
    from django.contrib.auth import get_user_model

    # Fetch the users
    users = User.objects.filter(id__in=user_ids)

    # Update the WebSocket chat rooms for the user
    for user in users:
        group_name = get_user_chat_room_group(user)
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_updated_rooms",
            },
        )

    return
