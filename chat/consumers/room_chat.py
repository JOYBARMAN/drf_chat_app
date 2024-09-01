import json
import logging

from django.contrib.auth import get_user_model

from chat.models import ChatRoom

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)


class RoomChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept connection
        await self.accept()
        # Check if error exists during connection
        if self.is_error_exists():
            error = {"error": str(self.scope["error"])}
            await self.send(text_data=json.dumps(error))
            await self.close()
            return
        # Get the room name from url
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # Check room existance under this room name
        if await self.check_room_existance(self.room_name):
            # Add to the group
            self.group_name = self.room_name
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )
        else:
            error_message = "Invalid room name"
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close()

    async def receive(self, text_data=None):
        # Send real time chat message
        await self.channel_layer.group_send(
            self.group_name, {"type": "chat_message", "message": text_data}
        )

    async def disconnect(self, close_code):
        # Remove from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        logger.warning(f"disconnected {close_code}")

        await self.close()

    async def check_room_existance(self, room_name: str):
        """Check room exists in database"""
        return await database_sync_to_async(
            ChatRoom.objects.filter(name=room_name).exists
        )()

    async def chat_message(self, event):
        """Send the message to WebSocket"""
        await self.send(text_data=event["message"])

    def is_error_exists(self):
        """Checks if error exists during websockets"""
        return True if "error" in self.scope else False
