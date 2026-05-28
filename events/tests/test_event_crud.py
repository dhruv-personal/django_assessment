from datetime import timedelta

from django.utils import timezone

import pytest

from events.models import Event


@pytest.mark.django_db
class TestEventCRUD:

    def test_create_event(self, api_client, facilitator_user):
        api_client.force_authenticate(user=facilitator_user)

        data = {
            "title": "New Event",
            "description": "New Description",
            "language": "English",
            "location": "New Location",
            "starts_at": (timezone.now() + timedelta(days=1)).isoformat(),
            "ends_at": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
            "capacity": 20,
        }

        response = api_client.post("/facilitator/events/", data, format="json")

        assert response.status_code == 201
        assert response.data["title"] == "New Event"
        assert Event.objects.filter(title="New Event").exists()

    def test_list_facilitator_events(self, api_client, facilitator_user, sample_event):
        api_client.force_authenticate(user=facilitator_user)

        response = api_client.get("/facilitator/events/")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_update_event(self, api_client, facilitator_user, sample_event):
        api_client.force_authenticate(user=sample_event.created_by)

        data = {"title": "Updated Event Title"}

        response = api_client.patch(f"/facilitator/events/{sample_event.id}/", data, format="json")

        assert response.status_code == 200
        assert response.data["title"] == "Updated Event Title"

    def test_delete_event(self, api_client, facilitator_user, sample_event):
        api_client.force_authenticate(user=sample_event.created_by)

        response = api_client.delete(f"/facilitator/events/{sample_event.id}/")

        assert response.status_code == 204
        assert not Event.objects.filter(id=sample_event.id).exists()

    def test_event_with_enrollments_stats(self, api_client, facilitator_user, sample_event, sample_enrollment):
        api_client.force_authenticate(user=sample_event.created_by)

        response = api_client.get(f"/facilitator/events/{sample_event.id}/")

        assert response.status_code == 200
        assert response.data["total_enrollments"] == 1
        assert response.data["available_seats"] == 9
