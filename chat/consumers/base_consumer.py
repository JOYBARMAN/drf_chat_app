import json

from django.contrib.auth import get_user_model
from django.core.cache import cache

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from shared.cache_key import get_room_connected_users_cache_key


User = get_user_model()


class BaseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        pass

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def get_user(self, username=None, user_id=None):
        """Get the user instance from the database."""
        error_message = None
        try:
            if username:
                error_message = (
                    f"Receiver with username {username} does not exist in the system"
                )
                return await database_sync_to_async(User.objects.get)(username=username)
            if user_id:
                error_message = f"Requested user does not exist in the system"
                return await database_sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({"error": error_message}))
            await self.close()
            return

    async def chat_message(self, event):
        """Send the message to WebSocket"""
        await self.send(text_data=event["message"])

    async def validate_message(self, text_data):
        """Validate the send message"""
        try:
            # Parse the received text data as JSON
            data = json.loads(text_data)
            return data
        except json.JSONDecodeError:
            error_message = "Message format must be {'message':'your message'} "
            await self.send(text_data=json.dumps({"error": error_message}))
            return None

    def is_error_exists(self):
        """Checks if error exists during websockets"""
        return True if "error" in self.scope else False
