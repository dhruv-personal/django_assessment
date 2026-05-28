"""
Serializers for authentication.
"""

import logging

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import UserProfile
from authentication.utils import validate_otp
from events_platform.constants import (
    ERROR_CODE_EMAIL_NOT_VERIFIED,
    ERROR_CODE_INVALID_CREDENTIALS,
    ERROR_CODE_OTP_EXPIRED,
    ERROR_CODE_OTP_INVALID,
    ERROR_CODE_OTP_MAX_ATTEMPTS,
    ERROR_CODE_USER_NOT_FOUND,
)

logger = logging.getLogger(__name__)


class SignupSerializer(serializers.Serializer):
    """
    Serializer for user signup.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)

    def validate_email(self, value):
        """
        Validate that email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value.lower()

    def create(self, validated_data):
        """
        Create new user with the provided data.
        """
        email = validated_data["email"]
        password = validated_data["password"]
        role = validated_data["role"]

        user = User.objects.create_user(username=email, email=email, password=password)

        user._profile_role = role

        if hasattr(user, "profile"):
            user.profile.role = role
            user.profile.save()
        else:
            UserProfile.objects.create(user=user, role=role)

        logger.info(f"User created: {email} with role {role}")

        return user


class VerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)

    def validate(self, data):
        """
        Validate OTP and email.
        """
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "User not found", "code": ERROR_CODE_USER_NOT_FOUND})

        is_valid, message = validate_otp(user, data["otp"])

        if not is_valid:
            error_code = ERROR_CODE_OTP_EXPIRED
            if "expired" in message.lower():
                error_code = ERROR_CODE_OTP_EXPIRED
            elif "invalid" in message.lower():
                error_code = ERROR_CODE_OTP_INVALID
            elif "attempts" in message.lower():
                error_code = ERROR_CODE_OTP_MAX_ATTEMPTS
            else:
                error_code = "otp_error"

            raise serializers.ValidationError({"detail": message, "code": error_code})

        data["user"] = user
        return data

    def save(self):
        """
        Mark user as verified.
        """
        user = self.validated_data["user"]
        user.profile.email_verified = True
        user.profile.save()
        logger.info(f"Email verified for user: {user.email}")
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        """
        Validate login credentials.
        """
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials", "code": ERROR_CODE_INVALID_CREDENTIALS})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid credentials", "code": ERROR_CODE_INVALID_CREDENTIALS})

        if not user.profile.email_verified:
            raise serializers.ValidationError(
                {
                    "detail": "Email not verified. Please verify your email first",
                    "code": ERROR_CODE_EMAIL_NOT_VERIFIED,
                }
            )

        data["user"] = user
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that uses email instead of username.
    """

    username_field = "email"

    def validate(self, attrs):
        """
        Validate and return JWT tokens.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
            attrs["username"] = user.username
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials", "code": ERROR_CODE_INVALID_CREDENTIALS})

        if not user.profile.email_verified:
            raise serializers.ValidationError(
                {
                    "detail": "Email not verified. Please verify your email first",
                    "code": ERROR_CODE_EMAIL_NOT_VERIFIED,
                }
            )

        data = super().validate(attrs)

        data["user"] = {
            "email": user.email,
            "role": user.profile.role,
        }

        logger.info(f"User logged in: {user.email}")

        return data
