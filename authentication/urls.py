"""
URL configuration for authentication app.
"""

from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import (
    CustomTokenObtainPairView,
    ResendOTPView,
    SignupView,
    VerifyEmailView,
)

urlpatterns = [
    path("signup", SignupView.as_view(), name="signup"),
    path("verify-email", VerifyEmailView.as_view(), name="verify_email"),
    path("login", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("resend-otp", ResendOTPView.as_view(), name="resend_otp"),
]
