from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # very basic email+password login for the demo
        email = (request.data.get("email") or "").lower().strip()
        password = request.data.get("password") or ""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=400)
        if not user.check_password(password):
            return Response({"detail": "Invalid credentials."}, status=400)

        tokens = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "user": {"id": user.id, "email": user.email},
            }
        )


class SignupView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "signup"

    def post(self, request):
        s = SignupSerializer(data=request.data)
        if not s.is_valid():
            return Response({"errors": s.errors}, status=400)
        user = s.save()
        return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)
