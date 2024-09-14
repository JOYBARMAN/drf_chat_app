from django.contrib.auth import get_user_model

from rest_framework import serializers

from chat.models import BlockList


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        read_only_fields = fields


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

    def create(self, validated_data):
        user = User.objects.get(id=validated_data["user_uid"])
        block_list = BlockList.objects.create(user=user)
        return block_list