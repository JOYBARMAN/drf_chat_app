from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from accounts.rest.serializers.accounts import UserRegisterSerializer


class UserRegisterView(CreateAPIView):
    """User registration view"""

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
