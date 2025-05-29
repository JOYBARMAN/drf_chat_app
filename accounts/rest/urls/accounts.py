from django.urls import path, include, re_path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.rest.views.accounts import UserRegisterView


urlpatterns = [
    path("/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("/register", UserRegisterView.as_view(), name="user_register"),
]
