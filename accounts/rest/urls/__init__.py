from django.urls import path, include


urlpatterns = [
    path("", include("accounts.rest.urls.accounts")),
    path("/verify", include("accounts.rest.urls.verify")),
]
