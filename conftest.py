"""
Pytest configuration and fixtures for testing.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

import pytest

from authentication.models import UserProfile
from events.models import Enrollment, Event
from events_platform.constants import (
    ENROLLMENT_STATUS_ENROLLED,
    USER_ROLE_FACILITATOR,
    USER_ROLE_SEEKER,
)


@pytest.fixture
def seeker_user(db):
    """
    Create a verified seeker user for testing.
    """
    user = User.objects.create_user(username="seeker@test.com", email="seeker@test.com", password="testpass123")
    UserProfile.objects.create(user=user, role=USER_ROLE_SEEKER, email_verified=True)
    return user


@pytest.fixture
def facilitator_user(db):
    """
    Create a verified facilitator user for testing.
    """
    user = User.objects.create_user(
        username="facilitator@test.com", email="facilitator@test.com", password="testpass123"
    )
    UserProfile.objects.create(user=user, role=USER_ROLE_FACILITATOR, email_verified=True)
    return user


@pytest.fixture
def unverified_user(db):
    """
    Create an unverified seeker user for testing.
    """
    user = User.objects.create_user(username="unverified@test.com", email="unverified@test.com", password="testpass123")
    UserProfile.objects.create(user=user, role=USER_ROLE_SEEKER, email_verified=False)
    return user


@pytest.fixture
def sample_event(db, facilitator_user):
    """
    Create a sample event for testing.
    """
    return Event.objects.create(
        title="Test Event",
        description="Test Description",
        language="English",
        location="Test Location",
        starts_at=timezone.now() + timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=1, hours=2),
        capacity=10,
        created_by=facilitator_user,
    )


@pytest.fixture
def sample_enrollment(db, sample_event, seeker_user):
    """
    Create a sample enrollment for testing.
    """
    return Enrollment.objects.create(event=sample_event, seeker=seeker_user, status=ENROLLMENT_STATUS_ENROLLED)


@pytest.fixture
def api_client():
    """
    Create DRF API client for testing.
    """
    from rest_framework.test import APIClient

    return APIClient()
