from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

import pytest

from events.models import Enrollment, Event


@pytest.mark.django_db
class TestEnrollment:

    @patch("events.views.send_followup_email.apply_async")
    def test_create_enrollment(self, mock_task, api_client, seeker_user, sample_event):
        api_client.force_authenticate(user=seeker_user)

        data = {"event": sample_event.id}

        response = api_client.post("/enrollments/", data, format="json")

        assert response.status_code == 201
        assert Enrollment.objects.filter(seeker=seeker_user, event=sample_event).exists()
        mock_task.assert_called_once()

    def test_cannot_enroll_twice(self, api_client, seeker_user, sample_enrollment):
        api_client.force_authenticate(user=seeker_user)

        data = {"event": sample_enrollment.event.id}

        response = api_client.post("/enrollments/", data, format="json")

        assert response.status_code == 400
        assert "already enrolled" in response.data["detail"].lower()

    def test_cannot_enroll_in_full_event(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        full_event = Event.objects.create(
            title="Full Event",
            description="Description",
            language="English",
            location="Location",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            capacity=1,
            created_by=facilitator_user,
        )

        other_seeker = seeker_user
        Enrollment.objects.create(event=full_event, seeker=other_seeker)

        from django.contrib.auth.models import User

        from authentication.models import UserProfile

        new_seeker = User.objects.create_user(
            username="newseeker@test.com", email="newseeker@test.com", password="testpass123"
        )
        UserProfile.objects.create(user=new_seeker, role=UserProfile.SEEKER, email_verified=True)

        api_client.force_authenticate(user=new_seeker)

        data = {"event": full_event.id}

        response = api_client.post("/enrollments/", data, format="json")

        assert response.status_code == 400
        assert "full" in response.data["detail"].lower()

    def test_list_past_enrollments(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        past_event = Event.objects.create(
            title="Past Event",
            description="Description",
            language="English",
            location="Location",
            starts_at=timezone.now() - timedelta(days=2),
            ends_at=timezone.now() - timedelta(days=2, hours=-2),
            created_by=facilitator_user,
        )

        Enrollment.objects.create(event=past_event, seeker=seeker_user)

        response = api_client.get("/enrollments/past/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_list_upcoming_enrollments(self, api_client, seeker_user, sample_enrollment):
        api_client.force_authenticate(user=seeker_user)

        response = api_client.get("/enrollments/upcoming/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
