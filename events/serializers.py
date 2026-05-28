"""
Serializers for events app.
"""

import logging

from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from events.models import Enrollment, Event
from events_platform.constants import (
    ENROLLMENT_STATUS_ENROLLED,
    ERROR_CODE_ALREADY_ENROLLED,
    ERROR_CODE_EVENT_FULL,
    ERROR_CODE_PAST_EVENT,
)

logger = logging.getLogger(__name__)


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event model (Seeker view).
    """

    available_seats = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "language",
            "location",
            "starts_at",
            "ends_at",
            "capacity",
            "available_seats",
            "is_full",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by_email"]

    def get_available_seats(self, obj):
        """
        Get available seats for the event.
        """
        return obj.available_seats()

    def get_is_full(self, obj):
        """
        Check if event is full.
        """
        return obj.is_full()

    def validate(self, data):
        """
        Validate event data.
        """
        if data.get("ends_at") and data.get("starts_at"):
            if data["ends_at"] <= data["starts_at"]:
                raise serializers.ValidationError(
                    {"detail": "End time must be after start time", "code": "invalid_time_range"}
                )

        if data.get("capacity") is not None and data["capacity"] < 0:
            raise serializers.ValidationError({"detail": "Capacity cannot be negative", "code": "invalid_capacity"})

        return data


class FacilitatorEventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event model (Facilitator view with enrollment stats).
    """

    total_enrollments = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "language",
            "location",
            "starts_at",
            "ends_at",
            "capacity",
            "total_enrollments",
            "available_seats",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_total_enrollments(self, obj):
        """
        Get total number of enrollments.
        """
        return obj.enrollments.filter(status=ENROLLMENT_STATUS_ENROLLED).count()

    def get_available_seats(self, obj):
        """
        Get available seats.
        """
        return obj.available_seats()

    def validate(self, data):
        """
        Validate event data.
        """
        if data.get("ends_at") and data.get("starts_at"):
            if data["ends_at"] <= data["starts_at"]:
                raise serializers.ValidationError(
                    {"detail": "End time must be after start time", "code": "invalid_time_range"}
                )

        if data.get("capacity") is not None and data["capacity"] < 0:
            raise serializers.ValidationError({"detail": "Capacity cannot be negative", "code": "invalid_capacity"})

        return data


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model (create action).
    """

    event_title = serializers.CharField(source="event.title", read_only=True)
    event_starts_at = serializers.DateTimeField(source="event.starts_at", read_only=True)
    event_ends_at = serializers.DateTimeField(source="event.ends_at", read_only=True)
    event_location = serializers.CharField(source="event.location", read_only=True)
    seeker_email = serializers.EmailField(source="seeker.email", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "event",
            "event_title",
            "event_starts_at",
            "event_ends_at",
            "event_location",
            "seeker_email",
            "status",
            "enrolled_at",
            "updated_at",
        ]
        read_only_fields = ["id", "seeker_email", "enrolled_at", "updated_at"]

    def validate_event(self, value):
        """
        Validate event is not in the past and not full.
        """
        if value.starts_at < timezone.now():
            raise serializers.ValidationError({"detail": "Cannot enroll in past events", "code": ERROR_CODE_PAST_EVENT})

        if value.is_full():
            raise serializers.ValidationError({"detail": "Event is full", "code": ERROR_CODE_EVENT_FULL})

        return value

    def validate(self, data):
        """
        Validate enrollment data.
        """
        request = self.context.get("request")
        event = data.get("event")

        if request and event:
            existing_enrollment = Enrollment.objects.filter(
                event=event, seeker=request.user, status=ENROLLMENT_STATUS_ENROLLED
            ).exists()

            if existing_enrollment:
                raise serializers.ValidationError(
                    {
                        "detail": "You are already enrolled in this event",
                        "code": ERROR_CODE_ALREADY_ENROLLED,
                    }
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create enrollment with database locking to prevent race conditions.
        """
        event = validated_data["event"]

        event_locked = Event.objects.select_for_update().get(id=event.id)

        if event_locked.is_full():
            raise serializers.ValidationError({"detail": "Event is full", "code": ERROR_CODE_EVENT_FULL})

        enrollment = Enrollment.objects.create(**validated_data)
        logger.info(f"Enrollment created: {enrollment.seeker.email} for event {event.title}")

        return enrollment


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model (list/retrieve actions with nested event).
    """

    event = EventSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "event", "status", "enrolled_at", "updated_at"]
        read_only_fields = ["id", "enrolled_at", "updated_at"]
