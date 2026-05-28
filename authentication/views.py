"""
Authentication views for the Events Platform.
"""

import logging

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.serializers import (
    CustomTokenObtainPairSerializer,
    SignupSerializer,
    VerifyEmailSerializer,
)
from authentication.utils import create_and_send_otp
from events_platform.constants import (
    ERROR_CODE_USER_NOT_FOUND,
)

logger = logging.getLogger(__name__)


class SignupView(APIView):
    """
    API view for user registration.
    Creates a new user and sends OTP for email verification.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user signup request.
        """
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user created: {user.email}")

            try:
                create_and_send_otp(user)
                logger.info(f"OTP sent to user: {user.email}")

                return Response(
                    {
                        "detail": "User created successfully. OTP sent to email",
                        "code": "signup_success",
                        "email": user.email,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"Failed to send OTP to {user.email}: {str(e)}")
                return Response(
                    {
                        "detail": f"User created but failed to send OTP: {str(e)}",
                        "code": "otp_send_failed",
                    },
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    API view for email verification using OTP.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Verify user email with OTP.
        """
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Email verified for user: {user.email}")

            return Response(
                {
                    "detail": "Email verified successfully. You can now login",
                    "code": "email_verified",
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view.
    """

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class ResendOTPView(APIView):
    """
    API view for resending OTP to user email.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Resend OTP to the provided email address.
        """
        email = request.data.get("email")

        if not email:
            return Response(
                {"detail": "Email is required", "code": "email_required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)

            if user.profile.email_verified:
                return Response(
                    {"detail": "Email already verified", "code": "already_verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            create_and_send_otp(user)
            logger.info(f"OTP resent to user: {user.email}")

            return Response(
                {"detail": "OTP sent successfully", "code": "otp_sent"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            logger.warning(f"Attempt to resend OTP to non-existent user: {email}")
            return Response(
                {"detail": "User not found", "code": ERROR_CODE_USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Failed to resend OTP to {email}: {str(e)}")
            return Response(
                {"detail": f"Failed to send OTP: {str(e)}", "code": "otp_send_failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
