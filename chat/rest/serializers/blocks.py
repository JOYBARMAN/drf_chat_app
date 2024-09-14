from django.contrib.auth import get_user_model

from rest_framework import serializers

from chat.models import BlockList, ChatRoom, ChatRoomMembership
from chat.rest.serializers.friends import UserSerializer
from chat.rest.serializers.chat_rooms import ChatRoomMembershipSerializer
from chat.choices import MemberShipStatusChoices


User = get_user_model()


class BlockListSerializer(serializers.ModelSerializer):
    user_uid = serializers.UUIDField(write_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = BlockList
        fields = [
            "uid",
            "user",
            "user_uid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def validate_user_uid(self, value):
        """Check if the user exists"""
        user = User.objects.filter(uid=value).first()
        if not user:
            raise serializers.ValidationError("User does not exist.")

        self.user = user

        return value

    def create(self, validated_data):
        requested_user = self.context["request"].user
        # Get or create block instance
        block_instance, created = BlockList.objects.get_or_create(
            user=self.user, blocked_by=requested_user
        )
        return block_instance


class BlockRoomMemberSerializer(serializers.ModelSerializer):
    user_uid = serializers.UUIDField(write_only=True)
    member_ship = ChatRoomMembershipSerializer(read_only=True)
    blocked_by = UserSerializer(read_only=True)

    class Meta:
        model = BlockList
        fields = [
            "uid",
            "member_ship",
            "blocked_by",
            "user_uid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_chat_room_instance(self, obj):
        room_uid = self.context["view"].kwargs.get("room_uid")
        chat_room = ChatRoom.objects.filter(uid=room_uid).first()

        if not chat_room:
            raise serializers.ValidationError("Chat room does not exist.")

        return chat_room

    def validate_user_uid(self, value):
        """Check if the user exists"""
        self.user = User.objects.filter(uid=value).first()
        if not self.user:
            raise serializers.ValidationError("User does not exist.")

        # Check if the user is a member of the chat room
        chat_room = self.get_chat_room_instance(self)
        self.chat_room_membership = ChatRoomMembership.objects.filter(
            user=self.user, chat_room=chat_room
        ).first()
        if not self.chat_room_membership:
            raise serializers.ValidationError("User is not a member of the chat room.")

        return value

    def create(self, validated_data):
        requested_user = self.context["request"].user
        # Get or create block instance
        block_instance, created = BlockList.objects.get_or_create(
            blocked_by=requested_user, member_ship=self.chat_room_membership
        )
        # Update the user membership status
        self.chat_room_membership.member_status = MemberShipStatusChoices.BLOCKED
        self.chat_room_membership.save_dirty_fields()

        return block_instance
