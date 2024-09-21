from django.urls import path, include

urlpatterns = [
    path("", include("chat.rest.urls.friends")),
    path("/blocked", include("chat.rest.urls.blocks")),
    path("/chat-room", include("chat.rest.urls.chat_rooms")),
]
