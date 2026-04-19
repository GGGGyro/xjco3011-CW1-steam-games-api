"""
Custom django-filter FilterSets for the Steam Games API.
Enables fine-grained query parameter filtering on the /games/ endpoint.
"""

import django_filters
from .models import Game


class GameFilter(django_filters.FilterSet):
    """
    FilterSet for the Game model.

    Supported query parameters:
      - genre          : case-insensitive substring match on genres field
      - developer      : case-insensitive substring match on developer field
      - publisher      : case-insensitive substring match on publisher field
      - platform       : case-insensitive substring match on platforms field
      - tag            : case-insensitive substring match on steamspy_tags field
      - min_price      : minimum price (inclusive)
      - max_price      : maximum price (inclusive)
      - free           : boolean filter for free-to-play games (price=0)
      - min_approval   : minimum approval rate (computed as positive / total * 100)
      - release_after  : games released on or after this date (YYYY-MM-DD)
      - release_before : games released on or before this date (YYYY-MM-DD)
      - required_age   : exact match on required_age field
      - max_age        : games with required_age <= this value
    """

    genre = django_filters.CharFilter(field_name='genres', lookup_expr='icontains')
    developer = django_filters.CharFilter(field_name='developer', lookup_expr='icontains')
    publisher = django_filters.CharFilter(field_name='publisher', lookup_expr='icontains')
    platform = django_filters.CharFilter(field_name='platforms', lookup_expr='icontains')
    tag = django_filters.CharFilter(field_name='steamspy_tags', lookup_expr='icontains')

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    free = django_filters.BooleanFilter(method='filter_free')

    release_after = django_filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_before = django_filters.DateFilter(field_name='release_date', lookup_expr='lte')

    required_age = django_filters.NumberFilter(field_name='required_age', lookup_expr='exact')
    max_age = django_filters.NumberFilter(field_name='required_age', lookup_expr='lte')

    min_positive = django_filters.NumberFilter(field_name='positive_ratings', lookup_expr='gte')

    class Meta:
        model = Game
        fields = [
            'genre', 'developer', 'publisher', 'platform', 'tag',
            'min_price', 'max_price', 'free',
            'release_after', 'release_before',
            'required_age', 'max_age',
            'min_positive',
        ]

    def filter_free(self, queryset, name, value):
        """Filter for free-to-play (price=0) or paid (price>0) games."""
        if value:
            return queryset.filter(price=0)
        return queryset.filter(price__gt=0)
