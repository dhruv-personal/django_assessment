"""
Custom permissions for events app.
"""

from rest_framework import permissions


class IsEventOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the event.
    """

    message = "You do not have permission to modify this event"

    def has_object_permission(self, request, view, obj):
        """
        Check if user is the event owner.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.created_by == request.user


class IsEnrollmentOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the enrollment.
    """

    message = "You can only view your own enrollments"

    def has_object_permission(self, request, view, obj):
        """
        Check if user is the enrollment owner.
        """
        return obj.seeker == request.user
