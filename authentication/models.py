"""
Authentication models for the Events Platform.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from events_platform.constants import (
    OTP_EXPIRY_MINUTES,
    OTP_MAX_ATTEMPTS,
    USER_ROLE_FACILITATOR,
    USER_ROLE_SEEKER,
)


class UserProfile(models.Model):
    """
    Extended user profile model with role and verification status.
    """

    ROLE_CHOICES = [
        (USER_ROLE_SEEKER, "Seeker"),
        (USER_ROLE_FACILITATOR, "Facilitator"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.role}"

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class OTP(models.Model):
    """
    One-Time Password model for email verification.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        super().save(*args, **kwargs)

    def is_valid(self):
        """
        Check if OTP is still valid.
        """
        return not self.is_used and timezone.now() < self.expires_at and self.attempts < OTP_MAX_ATTEMPTS

    def __str__(self):
        return f"OTP for {self.user.email} - {self.code}"

    class Meta:
        db_table = "otps"
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        ordering = ["-created_at"]
