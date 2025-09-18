from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.validators import RegexValidator

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        min_length=1, max_length=50,
        validators=[RegexValidator(r"^[A-Za-z ,.'-]+$")]
    )
    last_name = serializers.CharField(
        min_length=1, max_length=50,
        validators=[RegexValidator(r"^[A-Za-z ,.'-]+$")]
    )
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def validate_email(self, v):
        if User.objects.filter(email__iexact=v).exists():
            raise serializers.ValidationError("Email already registered.")
        return v.lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.username = validated_data["email"]  # simple username policy
        user.save()
        return user