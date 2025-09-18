from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    # MUST capture conv_id from the URL
    path("ws/chat/<int:conv_id>/", ChatConsumer.as_asgi()),
]
