import json, logging

from django.contrib.auth import get_user_model

from chat.consumers.base_consumer import BaseChatConsumer
from chat.utils import (
    get_chat_room_serialized_data,
)

from asgiref.sync import sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)


class UserChatRoomConsumer(BaseChatConsumer):
    async def connect(self):
        # Accept connection
        await self.accept()

        # Check if error exists during connection authentication related to user
        if self.is_error_exists():
            error = {"error": str(self.scope["error"])}
            await self.send(text_data=json.dumps(error))
            await self.close(code=4001)
            return

        # Get the user
        self.user = await self.get_user(user_id=self.scope.get("user_id", None))
        # Check user existence
        if not self.user:
            await self.close(code=4004)
            return

        # Add to the group
        self.group_name = f"user_{self.user.uid}_chat_rooms"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.receive()

    async def receive(self, text_data=None):
        # Extract the page and page_size from the received message
        data = json.loads(text_data or "{}")
        page = data.get("page", 1)
        page_size = data.get("page_size", 20)

        serialized_data = await sync_to_async(get_chat_room_serialized_data)(
            self.user, page, page_size
        )
        await self.send(text_data=json.dumps(serialized_data))

    async def send_updated_rooms(self, event):
        """Send updated chat rooms to the user"""
        await self.send(text_data=event["data"])

    async def disconnect(self, close_code):
        if close_code == 1000:
            # Remove user from the group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

        # Close the connection
        await self.close()
