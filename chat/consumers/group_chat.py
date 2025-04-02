import json, logging

from django.contrib.auth import get_user_model

from chat.models import ChatRoom, Message
from chat.consumers.base_consumer import BaseChatConsumer
from chat.utils import (
    update_message_cache,
    set_connected_user,
    get_room_connected_users,
    remove_connected_user,
)
from chat.rest.serializers.messages import MessageSerializer

from channels.db import database_sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)


class GroupChatConsumer(BaseChatConsumer):
    async def connect(self):
        # Accept connection
        await self.accept()

        # Check if error exists during connection authentication related to user
        if self.is_error_exists():
            error = {"error": str(self.scope["error"])}
            await self.send(text_data=json.dumps(error))
            await self.close(code=4001)
            return

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

    async def receive(self, text_data):
        data = await self.validate_message(text_data)

        # Close the connection if data is not valid
        if not data:
            return

        # Create message instance
        self.message_instance = await database_sync_to_async(Message.objects.create)(
            content=data["message"], sender=self.sender, chat_room=self.room
        )

        # Update real time message read by funtionality
        connected_user = get_room_connected_users(self.room_name)
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

    async def check_room_existance(self, room_name: str):
        """Check room exists in database"""
        return await database_sync_to_async(
            ChatRoom.objects.filter(name=room_name).first
        )()
