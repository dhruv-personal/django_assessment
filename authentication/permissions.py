"""
Custom permissions for authentication and authorization.
"""

from rest_framework import permissions

from authentication.models import UserProfile
from events_platform.constants import USER_ROLE_FACILITATOR, USER_ROLE_SEEKER


class IsSeekerRole(permissions.BasePermission):
    """
    Permission to check if user has Seeker role.
    """

    message = "Only seekers can access this resource"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.profile.role == USER_ROLE_SEEKER
        except UserProfile.DoesNotExist:
            return False


class IsFacilitatorRole(permissions.BasePermission):
    """
    Permission to check if user has Facilitator role.
    """

    message = "Only facilitators can access this resource"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.profile.role == USER_ROLE_FACILITATOR
        except UserProfile.DoesNotExist:
            return False


class IsVerified(permissions.BasePermission):
    """
    Permission to check if user's email is verified.
    """

    message = "Email verification required"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.profile.email_verified
        except UserProfile.DoesNotExist:
            return False
