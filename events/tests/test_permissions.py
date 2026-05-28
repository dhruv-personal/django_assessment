from datetime import timedelta

from django.utils import timezone

import pytest

from events.models import Event


@pytest.mark.django_db
class TestPermissions:

    def test_seeker_cannot_create_event(self, api_client, seeker_user):
        api_client.force_authenticate(user=seeker_user)

        data = {
            "title": "Test Event",
            "description": "Test Description",
            "language": "English",
            "location": "Test Location",
            "starts_at": (timezone.now() + timedelta(days=1)).isoformat(),
            "ends_at": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
            "capacity": 10,
        }

        response = api_client.post("/facilitator/events/", data, format="json")

        assert response.status_code == 403

    def test_facilitator_can_create_event(self, api_client, facilitator_user):
        api_client.force_authenticate(user=facilitator_user)

        data = {
            "title": "Test Event",
            "description": "Test Description",
            "language": "English",
            "location": "Test Location",
            "starts_at": (timezone.now() + timedelta(days=1)).isoformat(),
            "ends_at": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
            "capacity": 10,
        }

        response = api_client.post("/facilitator/events/", data, format="json")

        assert response.status_code == 201

    def test_facilitator_cannot_update_others_event(self, api_client, facilitator_user, sample_event):
        other_facilitator = facilitator_user
        api_client.force_authenticate(user=other_facilitator)

        data = {"title": "Updated Title"}

        response = api_client.patch(f"/facilitator/events/{sample_event.id}/", data, format="json")

        assert response.status_code == 404

    def test_seeker_can_search_events(self, api_client, seeker_user, sample_event):
        api_client.force_authenticate(user=seeker_user)

        response = api_client.get("/events/search/")

        assert response.status_code == 200

    def test_facilitator_cannot_search_events(self, api_client, facilitator_user, sample_event):
        api_client.force_authenticate(user=facilitator_user)

        response = api_client.get("/events/search/")

        assert response.status_code == 403
