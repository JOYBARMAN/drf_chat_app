import json, logging

from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async


from chat.consumers.base_consumer import BaseChatConsumer
from chat.models import ChatRoom, ChatRoomMembership, ChatRoomInvitation
from chat.utils import (
    generate_private_room_name,
    set_connected_user,
    remove_connected_user,
    chat_room_messages_query,
)
from chat.rest.serializers.messages import MessageSerializer
from chat.tasks import update_message_read_by


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
        # Definre user already connected or not to thr room
        self.initial_request = True
        # Send the messages to the user
        await self.receive(text_data=json.dumps({"page": 1, "page_size": 20}))

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
        data = await self.validate_text_data(text_data=text_data)
        # If error exists during message validation skipped sending message
        if not data:
            return

        # User messages data
        queryset = await database_sync_to_async(chat_room_messages_query)(self.room.uid)

        response = self.apply_paginations(
            queryset=queryset,
            serializer=MessageSerializer,
            page=data.get("page", 1),
            page_size=data.get("page_size", 20),
        )

        # If message instance is not created, send the paginated response
        await self.send(text_data=response)

        # Update read_by field for all messages if user have initial request
        if self.initial_request:
            message_ids = await database_sync_to_async(
                lambda: list(queryset.values_list("id", flat=True))
            )()
            if message_ids:
                update_message_read_by.delay(
                    message_ids,
                    user_id=self.sender.id,
                    room_uid=self.room.uid,
                    room_name=self.room.name,
                )
            # Set initial request to False
            self.initial_request = False

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

    async def chat_message(self, event):
        """Send the message to WebSocket"""
        await self.receive(text_data=json.dumps({"page": 1, "page_size": 20}))
