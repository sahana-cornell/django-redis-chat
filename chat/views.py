from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, connection
from .models import Conversation, ConversationMember
from .redis_utils import list_messages

class HealthView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        ok_db = True
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT 1;")
        except Exception:
            ok_db = False
        return Response({"ok": True, "db": ok_db})

class CreateConversation(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "conversations"
    def post(self, request):
        raw = request.data.get("member_ids", [])
        try:
            member_ids = [int(x) for x in raw]
        except Exception:
            return Response({"error":"member_ids must be an array of integers"}, status=400)
        me = int(request.user.id)
        if me not in member_ids:
            member_ids.append(me)
        with transaction.atomic():
            c = Conversation.objects.create()
            for uid in set(member_ids):
                ConversationMember.objects.create(conversation=c, user_id=uid)
        return Response({"conversation_id": c.id})

class ListConversations(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "conversations"
    def get(self, request):
        qs = Conversation.objects.filter(conversationmember__user=request.user).distinct()
        return Response({"conversations":[{"id":c.id} for c in qs]})

class ConversationHistory(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "messages-read"
    def get(self, request, conv_id, *args, **kwargs):
        try:
            limit = int(request.GET.get("limit", 50))
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=400)
        limit = max(1, min(limit, 200))  # clamp a bit
        return Response({"messages": list_messages(conv_id, limit)})
