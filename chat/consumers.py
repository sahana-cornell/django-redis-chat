import logging
import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from rest_framework_simplejwt.backends import TokenBackend

from .redis_utils import list_messages, append_message, check_ws_rate_limit
from .models import ConversationMember

wslog = logging.getLogger("chat.ws")


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # URL: /ws/chat/<conv_id>/?token=...
        self.conv_id = int(self.scope["url_route"]["kwargs"]["conv_id"])
        qs = parse_qs(self.scope.get("query_string", b"").decode())
        token = (qs.get("token") or [None])[0]
        if not token:
            await self.close(code=4001)
            return

        # Use Django SECRET_KEY for JWT verification
        tb = TokenBackend(algorithm="HS256", signing_key=settings.SECRET_KEY)
        try:
            data = tb.decode(token, verify=True)
        except Exception:
            await self.close(code=4002)
            return

        self.user_id = int(data.get("user_id") or data.get("user", 0))
        if not self.user_id:
            await self.close(code=4003)
            return

        # Only allow members of the conversation
        is_member = await self._is_member(self.conv_id, self.user_id)
        if not is_member:
            await self.close(code=4004)
            return

        self.group = f"chat.{self.conv_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        wslog.info(f"connect conv={self.conv_id} user={self.user_id}")

        # Send recent history
        history = list_messages(self.conv_id)
        await self.send_json({"type": "history", "messages": history})

    async def disconnect(self, code):
        wslog.info(
            f"disconnect conv={self.conv_id} user={getattr(self,'user_id','-')} code={code}"
        )
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        wslog.info(f"recv conv={self.conv_id} user={self.user_id} payload={content}")
        text = (content or {}).get("text", "").strip()
        if not text:
            return
        # Throttle
        allowed, retry_after = check_ws_rate_limit(self.user_id, self.conv_id)
        if not allowed:
            wslog.warning(
                f"throttle conv={self.conv_id} user={self.user_id} retry_after={retry_after}s"
            )
            await self.send_json(
                {
                    "type": "rate_limited",
                    "retry_after": retry_after,
                    "message": f"Too many messages. Try again in {retry_after}s.",
                }
            )
            return
        # Save to Redis
        saved = append_message(self.conv_id, user_id=self.user_id, text=text)

        # Fan out to everyone in the room
        await self.channel_layer.group_send(
            self.group,
            {"type": "broadcast.message", "message": saved},
        )

    async def broadcast_message(self, event):
        await self.send_json({"type": "message", "message": event["message"]})

    @staticmethod
    async def _is_member(conv_id, user_id):
        from asgiref.sync import sync_to_async

        def _check():
            return ConversationMember.objects.filter(
                conversation_id=conv_id, user_id=user_id
            ).exists()

        return await sync_to_async(_check)()
