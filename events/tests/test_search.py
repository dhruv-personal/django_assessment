from datetime import timedelta

from django.utils import timezone

import pytest

from events.models import Event


@pytest.mark.django_db
class TestEventSearch:

    def test_search_events(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        Event.objects.create(
            title="Python Workshop",
            description="Learn Python",
            language="English",
            location="New York",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            created_by=facilitator_user,
        )

        Event.objects.create(
            title="Java Workshop",
            description="Learn Java",
            language="Spanish",
            location="Madrid",
            starts_at=timezone.now() + timedelta(days=2),
            ends_at=timezone.now() + timedelta(days=2, hours=2),
            created_by=facilitator_user,
        )

        response = api_client.get("/events/search/")

        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_filter_by_language(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        Event.objects.create(
            title="Event 1",
            description="Description 1",
            language="English",
            location="Location 1",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            created_by=facilitator_user,
        )

        Event.objects.create(
            title="Event 2",
            description="Description 2",
            language="Spanish",
            location="Location 2",
            starts_at=timezone.now() + timedelta(days=2),
            ends_at=timezone.now() + timedelta(days=2, hours=2),
            created_by=facilitator_user,
        )

        response = api_client.get("/events/search/?language=English")

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["language"] == "English"

    def test_filter_by_location(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        Event.objects.create(
            title="Event 1",
            description="Description 1",
            language="English",
            location="New York",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            created_by=facilitator_user,
        )

        response = api_client.get("/events/search/?location=New")

        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_search_by_query(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        Event.objects.create(
            title="Python Workshop",
            description="Learn Python programming",
            language="English",
            location="Location",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            created_by=facilitator_user,
        )

        response = api_client.get("/events/search/?q=Python")

        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_ordering_by_starts_at(self, api_client, seeker_user, facilitator_user):
        api_client.force_authenticate(user=seeker_user)

        Event.objects.create(
            title="Event 2",
            description="Description",
            language="English",
            location="Location",
            starts_at=timezone.now() + timedelta(days=2),
            ends_at=timezone.now() + timedelta(days=2, hours=2),
            created_by=facilitator_user,
        )

        Event.objects.create(
            title="Event 1",
            description="Description",
            language="English",
            location="Location",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=2),
            created_by=facilitator_user,
        )

        response = api_client.get("/events/search/")

        assert response.status_code == 200
        assert response.data["results"][0]["title"] == "Event 1"
