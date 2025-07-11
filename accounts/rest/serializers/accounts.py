from rest_framework import serializers

from core.models import User, UserProfile

from shared.redis_bloom import (
    check_email_in_bloom_filter,
    check_username_in_bloom_filter,
)


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        ]

    def validate_username(self, value):
        """Validate the username"""
        # Check if username already exists in the Bloom filter
        if check_username_in_bloom_filter(username=value):
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Validate the email"""
        # Check if email already exists in the Bloom filter
        print(
            "Checking email in bloom filter",
            check_email_in_bloom_filter(email=value),
            value,
        )
        if check_email_in_bloom_filter(email=value):
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        """Validate the password"""
        # Check length of password
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters long"
            )
        # Check password match with confirm password
        if value != self.initial_data.get("confirm_password"):
            raise serializers.ValidationError(
                "Password and confirm password don't match"
            )
        return value

    def create(self, validated_data):
        """Create a new user"""
        # Remove confirm_password from validated_data
        validated_data.pop("confirm_password", None)

        return super().create(validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "uid",
            "photo",
            "bio",
            "date_of_birth",
            "gender",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "uid",
            "username",
            "username",
            "first_name",
            "last_name",
            "email",
            "last_login",
            "created_at",
            "updated_at",
            "profile",
        ]
        read_only_fields = fields
        ref_name = "AccountsUserWithProfileSerializer"
