from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from shared.redis_bloom import (
    check_email_in_bloom_filter,
    check_username_in_bloom_filter,
)


class VerifyEmailAndUsernameView(APIView):
    """View to verify email addresses and username"""

    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get("email", None)
        user_name = request.query_params.get("username", None)
        # Check if email and username are provided
        if not email and not user_name:
            return Response(
                {"error": "Email or username are required in query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check email existance
        if email and check_email_in_bloom_filter(email=email):
            return Response(
                {"message": "Email already exists."}, status=status.HTTP_409_CONFLICT
            )
        # Check username existance
        if user_name and check_username_in_bloom_filter(username=user_name):
            return Response(
                {"message": "Username already exists."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"message": "Verification successful."},
            status=status.HTTP_200_OK,
        )
