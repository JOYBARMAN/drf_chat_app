from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "username",
            "first_name",
            "last_name",
            "email",
            "last_login",
            "created_at",
        ]
        read_only_fields = fields
