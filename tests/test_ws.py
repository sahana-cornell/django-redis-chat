import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth.models import User

from config.asgi import application
from chat.models import Conversation, ConversationMember


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ws_basic_flow():
    # --- create user & token (DB work must be off the event loop) ---
    user = await database_sync_to_async(User.objects.create_user)(
        username="ws@example.com",
        email="ws@example.com",
        password="Pass1243!",
    )
    token = str(AccessToken.for_user(user))

    # --- create conversation & membership (DB work off loop) ---
    conv = await database_sync_to_async(Conversation.objects.create)()
    await database_sync_to_async(ConversationMember.objects.create)(
        conversation=conv, user=user
    )

    # --- connect to websocket ---
    path = f"/ws/chat/{conv.id}/?token={token}"
    comm = WebsocketCommunicator(application, path)
    connected, _ = await comm.connect()
    assert connected

    # Optional: server may send an initial history frame
    try:
        first = await comm.receive_json_from(timeout=1)
        assert first["type"] in {"history", "hello", "message"}
    except Exception:
        # It's fine if nothing arrives immediately
        pass

    # --- send a message ---
    await comm.send_json_to({"text": "hello from test"})

    # --- receive echo/broadcast back ---
    resp = await comm.receive_json_from(timeout=3)
    assert resp["type"] == "message"
    msg = resp["message"]
    assert msg["text"] == "hello from test"
    assert msg["user_id"] == user.id

    # --- clean up ---
    await comm.disconnect()
