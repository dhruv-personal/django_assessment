"""
Views for events app.
"""

import logging

from django.db.models import Count, Q
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsFacilitatorRole, IsSeekerRole
from events.filters import EventFilter
from events.models import Enrollment, Event
from events.permissions import IsEventOwner
from events.serializers import (
    EnrollmentDetailSerializer,
    EnrollmentSerializer,
    EventSerializer,
    FacilitatorEventSerializer,
)
from events_platform.constants import ENROLLMENT_STATUS_ENROLLED

logger = logging.getLogger(__name__)


class EventSearchView(ListAPIView):
    """
    API view for event search (Seeker only).
    Lists events with filtering, pagination, and ordering.
    """

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsSeekerRole]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EventFilter
    ordering_fields = ["starts_at", "created_at"]
    ordering = ["starts_at"]

    def get_queryset(self):
        """
        Return only future events.
        """
        return Event.objects.filter(starts_at__gte=timezone.now())


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for enrollment management (Seeker only).
    """

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsSeekerRole]

    def get_queryset(self):
        """
        Return enrollments for the authenticated user.
        """
        return Enrollment.objects.filter(seeker=self.request.user)

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action in ["list", "retrieve", "past", "upcoming"]:
            return EnrollmentDetailSerializer
        return EnrollmentSerializer

    def perform_create(self, serializer):
        """
        Create enrollment and trigger follow-up email task.
        """
        enrollment = serializer.save(seeker=self.request.user)

        from events.tasks import send_followup_email
        from events_platform.constants import FOLLOWUP_EMAIL_DELAY_SECONDS

        send_followup_email.apply_async(args=[enrollment.id], countdown=FOLLOWUP_EMAIL_DELAY_SECONDS)

        logger.info(f"Enrollment created for {self.request.user.email} in event {enrollment.event.title}")

    @action(detail=False, methods=["get"])
    def past(self, request):
        """
        List past enrollments (events that have ended).
        """
        past_enrollments = self.get_queryset().filter(event__ends_at__lt=timezone.now()).order_by("-event__ends_at")

        page = self.paginate_queryset(past_enrollments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(past_enrollments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """
        List upcoming enrollments (events that haven't started yet).
        """
        upcoming_enrollments = (
            self.get_queryset()
            .filter(event__starts_at__gt=timezone.now(), status=ENROLLMENT_STATUS_ENROLLED)
            .order_by("event__starts_at")
        )

        page = self.paginate_queryset(upcoming_enrollments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(upcoming_enrollments, many=True)
        return Response(serializer.data)


class FacilitatorEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event CRUD operations (Facilitator only).
    """

    serializer_class = FacilitatorEventSerializer
    permission_classes = [IsAuthenticated, IsFacilitatorRole, IsEventOwner]

    def get_queryset(self):
        """
        Return events created by the authenticated facilitator.
        """
        return Event.objects.filter(created_by=self.request.user).annotate(
            total_enrollments=Count("enrollments", filter=Q(enrollments__status=ENROLLMENT_STATUS_ENROLLED))
        )

    def perform_create(self, serializer):
        """
        Create event with the current user as creator.
        """
        event = serializer.save(created_by=self.request.user)
        logger.info(f"Event created: {event.title} by {self.request.user.email}")

    def update(self, request, *args, **kwargs):
        """
        Update event with ownership check.
        """
        event = self.get_object()

        if event.created_by != request.user:
            logger.warning(f"Unauthorized update attempt on event {event.id} by {request.user.email}")
            return Response(
                {
                    "detail": "You do not have permission to update this event",
                    "code": "permission_denied",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.info(f"Event updated: {event.title} by {request.user.email}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete event with ownership check.
        """
        event = self.get_object()

        if event.created_by != request.user:
            logger.warning(f"Unauthorized delete attempt on event {event.id} by {request.user.email}")
            return Response(
                {
                    "detail": "You do not have permission to delete this event",
                    "code": "permission_denied",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        logger.info(f"Event deleted: {event.title} by {request.user.email}")
        return super().destroy(request, *args, **kwargs)
