"""
Admin configuration for events models.
"""

from django.contrib import admin

from events.models import Enrollment, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for Event model.
    """

    list_display = (
        "title",
        "language",
        "location",
        "starts_at",
        "ends_at",
        "capacity",
        "created_by",
    )
    list_filter = ("language", "location", "starts_at")
    search_fields = ("title", "description", "location")
    date_hierarchy = "starts_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Enrollment model.
    """

    list_display = ("event", "seeker", "status", "enrolled_at", "reminder_sent")
    list_filter = ("status", "reminder_sent")
    search_fields = ("event__title", "seeker__email")
    date_hierarchy = "enrolled_at"
    readonly_fields = ("enrolled_at", "updated_at")
