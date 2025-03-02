import json
import logging

from django.contrib.auth import get_user_model

from chat.models import ChatRoom, Message, ChatRoomMembership, ChatRoomInvitation
from chat.utils import generate_private_room_name, update_message_cache
from chat.rest.serializers.messages import MessageSerializer

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)
CONNECTED_USERS = set()


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept connection
        await self.accept()
        # Check if error exists during connection
        if self.is_error_exists():
            error = {"error": str(self.scope["error"])}
            await self.send(text_data=json.dumps(error))
            await self.close()
            return

        # Get the sender, receiver and the room
        self.sender = await self.get_user(user_id=self.scope["user_id"])
        self.receiver = await self.get_user(
            username=self.scope["url_route"]["kwargs"]["username"]
        )
        self.room = await self.get_or_create_private_chat(self.sender, self.receiver)

        # Add to the group
        self.group_name = self.room.name
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # Add to connected user
        CONNECTED_USERS.add(self.sender.id)

    async def disconnect(self, close_code):
        # Remove user from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        logger.warning(f"disconnected {close_code}")

        # Remove user from connected user
        CONNECTED_USERS.remove(self.sender.id)

        await self.close()

    async def receive(self, text_data):
        data = await self.validate_message(text_data)
        # Close the connection if data is not valid
        if not data:
            await self.close()
            return

        # Create message instance
        self.message_instance = await database_sync_to_async(Message.objects.create)(
            content=data["message"], sender=self.sender, chat_room=self.room
        )

        # Update real time message read by funtionality
        if self.sender.id in CONNECTED_USERS and self.receiver.id in CONNECTED_USERS:
            await database_sync_to_async(self.message_instance.read_by.add)(
                self.sender, self.receiver
            )
        else:
            await database_sync_to_async(self.message_instance.read_by.add)(self.sender)

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

    async def get_user(self, username=None, user_id=None):
        if user_id:
            # As we are validating the user_id from the token, we can safely assume that the user exists
            return await database_sync_to_async(User.objects.get)(id=user_id)

        if username:
            # We handle error only for the username since we are using it in the URL
            try:
                return await database_sync_to_async(User.objects.get)(username=username)
            except User.DoesNotExist:
                error_message = f"{username} username not found in the database."
                await self.send(text_data=json.dumps({"error": error_message}))
                await self.close()
                return

    async def chat_message(self, event):
        """Send the message to WebSocket"""
        await self.send(text_data=event["message"])

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
