"""
Admin configuration for authentication models.
"""

from django.contrib import admin

from authentication.models import OTP, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.
    """

    list_display = ("user", "role", "email_verified", "created_at")
    list_filter = ("role", "email_verified")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """
    Admin interface for OTP model.
    """

    list_display = ("user", "code", "created_at", "expires_at", "attempts", "is_used")
    list_filter = ("is_used",)
    search_fields = ("user__email",)
    readonly_fields = ("created_at",)
