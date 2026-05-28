"""
Filters for event search functionality.
"""

from django.db.models import Q

import django_filters

from events.models import Event


class EventFilter(django_filters.FilterSet):
    """
    Filter set for event search with location, language, dates, and text search.
    """

    location = django_filters.CharFilter(lookup_expr="icontains")
    language = django_filters.CharFilter(lookup_expr="iexact")
    starts_after = django_filters.DateTimeFilter(field_name="starts_at", lookup_expr="gte")
    starts_before = django_filters.DateTimeFilter(field_name="starts_at", lookup_expr="lte")
    q = django_filters.CharFilter(method="search_title_description")

    class Meta:
        model = Event
        fields = ["location", "language", "starts_after", "starts_before", "q"]

    def search_title_description(self, queryset, name, value):
        """
        Search in both title and description fields.
        """
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))
