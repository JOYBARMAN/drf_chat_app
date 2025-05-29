import json, logging

from django.contrib.auth import get_user_model

from chat.consumers.base_consumer import BaseChatConsumer
from chat.models import ChatRoom, Message, ChatRoomMembership, ChatRoomInvitation
from chat.utils import (
    generate_private_room_name,
    update_message_cache,
    set_connected_user,
    get_room_connected_users,
    remove_connected_user,
)
from chat.rest.serializers.messages import MessageSerializer

from channels.db import database_sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)


class PrivateChatConsumer(BaseChatConsumer):
    async def connect(self):
        # Accept connection
        await self.accept_connection()

        # Get the sender, receiver
        self.sender = await self.get_user(user_id=self.scope.get("user_id", None))
        self.receiver = await self.get_user(
            username=self.scope.get("url_route", {})
            .get("kwargs", {})
            .get("username", None)
        )

        # Check sender and receiver
        if not self.sender or not self.receiver:
            await self.close(code=4004)
            return

        # Check user uniqueness
        if self.sender and self.receiver and self.sender == self.receiver:
            error = {"error": "Sender and Receiver are same user!"}
            await self.send(text_data=json.dumps(error))
            await self.close(code=4000)
            return

        # Get or create the room
        self.room = await self.get_or_create_private_chat(self.sender, self.receiver)

        # Add to the group
        self.group_name = self.room.name
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # Add to connected user
        set_connected_user(self.room.name, self.sender)

    async def disconnect(self, close_code):
        if close_code == 1000:
            # Remove user from the group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

            # Remove user from connected user
            remove_connected_user(self.room.name, self.sender)

        logger.warning(f"disconnected {close_code}")
        await self.close()

    async def receive(self, text_data):
        data = await self.validate_message(text_data)
        # If error exists during message validation skipped sending message
        if not data:
            return

        # Create message instance
        self.message_instance = await database_sync_to_async(Message.objects.create)(
            content=data["message"], sender=self.sender, chat_room=self.room
        )

        # Update real time message read by funtionality
        connected_user = get_room_connected_users(self.room.name)
        await database_sync_to_async(self.message_instance.read_by.add)(*connected_user)

        # Update the message cache
        queryset = await database_sync_to_async(update_message_cache)(self.room.uid)
        serializer = MessageSerializer(queryset[0])

        # Broadcast data to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": json.dumps(serializer.data),
            },
        )

    async def get_or_create_private_chat(self, sender, receiver):
        """Get or create a private chat room between two users."""
        room_name = generate_private_room_name(sender, receiver)
        room, created = await database_sync_to_async(ChatRoom.objects.get_or_create)(
            name=room_name
        )

        if created:
            # Create chat room invitation for both users
            await database_sync_to_async(ChatRoomInvitation.objects.get_or_create)(
                chat_room=room, sender=sender, receiver=receiver
            )
            # Create chat room membership for both users
            await database_sync_to_async(ChatRoomMembership.objects.get_or_create)(
                chat_room=room, user=sender, oponent_user=receiver
            )
            await database_sync_to_async(ChatRoomMembership.objects.get_or_create)(
                chat_room=room, user=receiver, oponent_user=sender
            )

        return room
