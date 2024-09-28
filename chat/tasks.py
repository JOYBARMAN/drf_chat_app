from chat.models import Message
from celery import shared_task
from chat.rest.serializers.messages import MessageSerializer


@shared_task
def update_message_read_by(message_ids, user_id):
    from django.contrib.auth import get_user_model
    from chat.models import Message

    User = get_user_model()

    # Fetch the user and messages
    user = User.objects.get(id=user_id)
    messages = Message.objects.filter(id__in=message_ids)

    # Update the read_by field for each message
    for message in messages:
        if user not in message.read_by.all():
            message.read_by.add(user)
