from django.urls import path
from .views import CreateConversation, ListConversations, ConversationHistory

urlpatterns = [
    path("conversations", CreateConversation.as_view(), name="conversations-create"),
    path("conversations/list", ListConversations.as_view(), name="conv-list"),
    path("conversations/<int:conv_id>/history", ConversationHistory.as_view(), name="conv-history"),
]
