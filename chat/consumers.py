import json
import logging

from django.contrib.auth import get_user_model


from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


User = get_user_model()
logger = logging.getLogger(__name__)


class PrivateChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Accept connection
        await self.accept()
    async def disconnect(self, close_code):
        pass
    async def receive(self, text_data):
        pass