"""
URL configuration for events app.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from events.views import EnrollmentViewSet, EventSearchView, FacilitatorEventViewSet

router = DefaultRouter()
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"facilitator/events", FacilitatorEventViewSet, basename="facilitator-event")

urlpatterns = [
    path("events/search/", EventSearchView.as_view(), name="event-search"),
    path("", include(router.urls)),
]
