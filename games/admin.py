"""Django Admin configuration for the Steam Games API."""

from django.contrib import admin
from django.utils.html import format_html
from .models import Game, Review


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin interface for the Game model."""

    list_display = (
        'name', 'developer', 'publisher', 'release_date',
        'price_display', 'is_free_badge', 'approval_rate_display',
        'positive_ratings', 'platforms',
    )
    list_filter = ('english', 'release_date', 'required_age')
    search_fields = ('name', 'developer', 'publisher', 'genres', 'steamspy_tags')
    ordering = ('-positive_ratings',)
    readonly_fields = ('created_at', 'updated_at', 'total_ratings', 'approval_rate', 'is_free')
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('appid', 'name', 'developer', 'publisher', 'release_date', 'required_age', 'english')
        }),
        ('Classification', {
            'fields': ('genres', 'categories', 'steamspy_tags', 'platforms')
        }),
        ('Pricing', {
            'fields': ('price', 'is_free')
        }),
        ('Ratings & Popularity', {
            'fields': ('positive_ratings', 'negative_ratings', 'total_ratings', 'approval_rate', 'owners')
        }),
        ('Playtime', {
            'fields': ('average_playtime', 'median_playtime', 'achievements')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        if obj.price == 0:
            return format_html('<span style="color: green;">Free</span>')
        return f'${obj.price}'
    price_display.short_description = 'Price'

    def is_free_badge(self, obj):
        if obj.is_free:
            return format_html('<span style="color: green; font-weight: bold;">✓ Free</span>')
        return format_html('<span style="color: grey;">Paid</span>')
    is_free_badge.short_description = 'Free to Play'

    def approval_rate_display(self, obj):
        rate = obj.approval_rate
        if rate is None:
            return '—'
        if rate >= 80:
            colour = 'green'
        elif rate >= 60:
            colour = 'orange'
        else:
            colour = 'red'
        rate_str = f'{rate:.1f}%'
        return format_html('<span style="color: {};">{}</span>', colour, rate_str)
    approval_rate_display.short_description = 'Approval Rate'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for the Review model."""

    list_display = (
        'game', 'user', 'rating', 'title', 'recommended', 'hours_played', 'created_at'
    )
    list_filter = ('recommended', 'rating', 'created_at')
    search_fields = ('title', 'body', 'user__username', 'game__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    raw_id_fields = ('game', 'user')

    fieldsets = (
        ('Review Details', {
            'fields': ('game', 'user', 'rating', 'title', 'body', 'recommended', 'hours_played')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
