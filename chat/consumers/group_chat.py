import json, logging

from django.contrib.auth import get_user_model

from chat.models import ChatRoom, Message
from chat.consumers.base_consumer import BaseChatConsumer
from chat.utils import (
    update_message_cache,
    set_connected_user,
    get_room_connected_users,
    remove_connected_user,
    chat_room_messages_query,
)
from chat.rest.serializers.messages import MessageSerializer
from chat.tasks import update_message_read_by

from channels.db import database_sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)


class GroupChatConsumer(BaseChatConsumer):
    async def connect(self):
        # Accept connection
        await self.accept_connection()

        # Get the sender, receiver
        self.sender = await self.get_user(user_id=self.scope.get("user_id", None))

        # Check sender
        if not self.sender:
            await self.close(code=4004)
            return

        # Get the room name from url
        self.room_name = (
            self.scope.get("url_route", {}).get("kwargs", {}).get("room_name", None)
        )
        # Get the room instance
        self.room = await self.check_room_existance(self.room_name)

        # Check room existance under this room name
        if not self.room:
            error = {"error": "Room does not exist in the system"}
            await self.send(text_data=json.dumps(error))
            await self.close(code=4004)
            return
        else:
            # Add to the group
            self.group_name = self.room.name
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )

        # Add to connected user
        set_connected_user(self.room_name, self.sender)
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
            remove_connected_user(self.room_name, self.sender)

        logger.warning(f"disconnected {close_code}")
        await self.close()

    async def receive(self, text_data):
        data = await self.validate_text_data(text_data=text_data)
        # Close the connection if data is not valid
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

    async def check_room_existance(self, room_name: str):
        """Check room exists in database"""
        return await database_sync_to_async(
            ChatRoom.objects.filter(name=room_name).first
        )()

    async def chat_message(self, event):
        """Send the message to WebSocket"""
        await self.receive(text_data=json.dumps({"page": 1, "page_size": 20}))
