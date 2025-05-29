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

    async def accept_connection(self):
        """Accept the WebSocket connection."""
        # Get the subprotocols from the scope
        subprotocols = self.scope.get("subprotocols")
        if subprotocols:
            await self.accept(subprotocol=subprotocols)
        else:
            await self.accept()

        # Check if error exists during connection authentication related to user
        if self.is_error_exists():
            error = {"error": str(self.scope["error"])}
            await self.send(text_data=json.dumps(error))
            await self.close(code=4001)
            return

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
            return

    async def chat_message(self, event):
        """Send the message to WebSocket"""
        await self.send(text_data=event["message"])

    async def validate_message(self, text_data):
        """Validate the received message"""
        try:
            # Parse the received text data as JSON
            data = json.loads(text_data)

            # Check if the data is a dictionary
            if not isinstance(data, dict):
                raise ValueError("Invalid format. Expected a JSON object.")

            # Check only message key exists in the data
            if set(data.keys()) != {"message"}:
                raise ValueError(
                    "Invalid format. Only {'message': 'your message'} is allowed."
                )

            # Check message key is not empty
            if not isinstance(data["message"], str) or not data["message"].strip():
                raise ValueError(
                    "Invalid format. 'message' must be a non-empty string."
                )

            return data

        except (json.JSONDecodeError, ValueError) as e:
            error_message = str(e)
            await self.send(text_data=json.dumps({"error": error_message}))
            return None

    def is_error_exists(self):
        """Checks if error exists during websockets"""
        return True if "error" in self.scope else False
