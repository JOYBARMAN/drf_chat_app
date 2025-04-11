import json

from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.models import Message
from chat.rest.serializers.messages import MessageSerializer
from chat.tasks import update_ws_chat_rooms

from asgiref.sync import async_to_sync


channel_layer = get_channel_layer()


@receiver(post_save, sender=Message)
def send_message_to_ws(sender, instance, created, **kwargs):
    """Signal to send message instance data to the WebSocket when a new message is created."""

    if created and instance.attachment:
        group_name = instance.chat_room.name

        # Serialize message data
        message_data = MessageSerializer(instance).data

        # Send message to the WebSocket group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat_message",
                "message": json.dumps(message_data),
            },
        )
    related_users = list(
        instance.chat_room.memberships.values_list("user__id", flat=True)
    )

    # Send updated chat rooms to all related users
    update_ws_chat_rooms.delay(related_users)
