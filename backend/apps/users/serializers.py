# Serializers for users and watchlist
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import CustomUser, Watchlist


class LoginSerializer(serializers.Serializer):
    """Login with email and password"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        
        data["user"] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ["email", "username", "password", "password2", "phone"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords match nahi kar rahe"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ["id", "email", "username", "phone", "date_joined"]
        read_only_fields = ["email", "date_joined"]


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Watchlist
        fields = ["id", "name", "symbols", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)