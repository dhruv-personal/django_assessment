"""
Event and Enrollment models for the Events Platform.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from events_platform.constants import (
    ENROLLMENT_STATUS_CANCELED,
    ENROLLMENT_STATUS_ENROLLED,
)


class Event(models.Model):
    """
    Event model representing an event that can be created by facilitators.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    language = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=200, db_index=True)
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField()
    capacity = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validate event data.
        """
        if self.ends_at and self.starts_at and self.ends_at <= self.starts_at:
            raise ValidationError("End time must be after start time")

        if self.capacity is not None and self.capacity < 0:
            raise ValidationError("Capacity cannot be negative")

    def available_seats(self):
        """
        Calculate available seats for the event.
        """
        if self.capacity is None:
            return None

        enrolled_count = self.enrollments.filter(status=ENROLLMENT_STATUS_ENROLLED).count()
        return max(0, self.capacity - enrolled_count)

    def is_full(self):
        """
        Check if event is at full capacity.
        """
        if self.capacity is None:
            return False

        return self.available_seats() == 0

    def __str__(self):
        return f"{self.title} - {self.starts_at}"

    class Meta:
        db_table = "events"
        ordering = ["starts_at"]
        indexes = [
            models.Index(fields=["starts_at"]),
            models.Index(fields=["language"]),
            models.Index(fields=["location"]),
            models.Index(fields=["starts_at", "language"]),
            models.Index(fields=["starts_at", "location"]),
        ]


class Enrollment(models.Model):
    """
    Enrollment model representing a seeker's enrollment in an event.
    """

    STATUS_CHOICES = [
        (ENROLLMENT_STATUS_ENROLLED, "Enrolled"),
        (ENROLLMENT_STATUS_CANCELED, "Canceled"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="enrollments")
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ENROLLMENT_STATUS_ENROLLED)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seeker.email} - {self.event.title} ({self.status})"

    class Meta:
        db_table = "enrollments"
        ordering = ["-enrolled_at"]
        unique_together = ["event", "seeker"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "seeker"],
                condition=models.Q(status=ENROLLMENT_STATUS_ENROLLED),
                name="unique_active_enrollment",
            )
        ]
        indexes = [
            models.Index(fields=["seeker", "status"]),
            models.Index(fields=["event", "status"]),
            models.Index(fields=["enrolled_at"]),
        ]
