import json

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

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

    # async def validate_message(self, text_data):
    #     """Validate the received message"""
    #     try:
    #         # Parse the received text data as JSON
    #         data = json.loads(text_data)

    #         # Check if the data is a dictionary
    #         if not isinstance(data, dict):
    #             raise ValueError("Invalid format. Expected a JSON object.")

    #         # Check only message key exists in the data
    #         allowed_keys = {"message", "page", "page_size"}
    #         if (allowed_keys - set(data.keys())) == allowed_keys:
    #             raise ValueError(
    #                 "Invalid format. Only {'message': 'your message', 'page':'page number', 'page_size':'Number of page size'} are allowed."
    #             )

    #         # Check message key is not empty
    #         message = data.get("message", None)
    #         if message:
    #             if not isinstance(data["message"], str) or not data["message"].strip():
    #                 raise ValueError(
    #                     "Invalid format. 'message' must be a non-empty string."
    #                 )

    #         return data

    #     except (json.JSONDecodeError, ValueError) as e:
    #         error_message = str(e)
    #         await self.send(text_data=json.dumps({"error": error_message}))
    #         return None

    async def validate_text_data(self, text_data):
        """Validate the received text data."""
        try:
            # Parse the received text data as JSON
            data = json.loads(text_data)

            # Check if the data is a dictionary
            if not isinstance(data, dict):
                raise ValueError("Invalid format. Expected a JSON object.")

            # Check only message key exists in the data
            allowed_keys = {"page", "page_size"}
            if (allowed_keys - set(data.keys())) == allowed_keys:
                raise ValueError(
                    "Invalid format. Only {'page':'page number', 'page_size':'Number of page size'} are allowed."
                )

            return data

        except (json.JSONDecodeError, ValueError) as e:
            error_message = str(e)
            await self.send(text_data=json.dumps({"error": error_message}))
            return None

    def apply_paginations(self, queryset=[], serializer=None, page=1, page_size=20):
        """Get the paginated response data"""
        # print("queryset", queryset.__dict__)
        paginator = Paginator(queryset, page_size)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serialized_data = serializer(page_obj.object_list, many=True).data

        data = {
            "pagination": {
                "page": page_obj.number,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
            },
            "results": serialized_data,
        }

        return json.dumps(data)

    def is_error_exists(self):
        """Checks if error exists during websockets"""
        return True if "error" in self.scope else False
