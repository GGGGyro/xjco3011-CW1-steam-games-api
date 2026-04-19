"""
Serializers for the Steam Games API.

Defines how model instances are converted to/from JSON representations,
including field-level validation and nested read-only representations.
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Game, Review


# ─────────────────────────────────────────────────────────────────────────────
# Game Serializers
# ─────────────────────────────────────────────────────────────────────────────

class GameListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used for list endpoints.
    Exposes only the fields needed for browsing/searching, keeping
    response payloads small and fast.
    """
    approval_rate = serializers.ReadOnlyField()
    is_free = serializers.ReadOnlyField()
    total_ratings = serializers.ReadOnlyField()

    class Meta:
        model = Game
        fields = [
            'id', 'appid', 'name', 'release_date',
            'developer', 'publisher', 'genres', 'platforms',
            'price', 'is_free', 'positive_ratings', 'negative_ratings',
            'total_ratings', 'approval_rate', 'owners',
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer used for retrieve, create, and update operations.
    Includes all fields plus computed properties.
    """
    approval_rate = serializers.ReadOnlyField()
    is_free = serializers.ReadOnlyField()
    total_ratings = serializers.ReadOnlyField()
    genre_list = serializers.ReadOnlyField()
    platform_list = serializers.ReadOnlyField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'id', 'appid', 'name', 'release_date',
            'developer', 'publisher', 'platforms', 'platform_list',
            'required_age', 'english',
            'categories', 'genres', 'genre_list', 'steamspy_tags',
            'achievements',
            'positive_ratings', 'negative_ratings', 'total_ratings', 'approval_rate',
            'average_playtime', 'median_playtime',
            'owners', 'price', 'is_free',
            'review_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_review_count(self, obj):
        return obj.reviews.count()

    def validate_appid(self, value):
        """Ensure appid is positive."""
        if value <= 0:
            raise serializers.ValidationError("appid must be a positive integer.")
        return value

    def validate_price(self, value):
        """Ensure price is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate(self, attrs):
        """Cross-field validation: positive_ratings + negative_ratings must be consistent."""
        pos = attrs.get('positive_ratings', 0)
        neg = attrs.get('negative_ratings', 0)
        if pos < 0 or neg < 0:
            raise serializers.ValidationError(
                "Rating counts must be non-negative integers."
            )
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# Review Serializers
# ─────────────────────────────────────────────────────────────────────────────

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review objects.
    The `user` field is automatically set to the authenticated request user
    and is read-only in responses.
    """
    username = serializers.ReadOnlyField(source='user.username')
    game_name = serializers.ReadOnlyField(source='game.name')

    class Meta:
        model = Review
        fields = [
            'id', 'game', 'game_name',
            'user', 'username',
            'rating', 'title', 'body',
            'hours_played', 'recommended',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value

    def create(self, validated_data):
        """Automatically assign the authenticated user as the review author."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ─────────────────────────────────────────────────────────────────────────────
# Auth Serializers
# ─────────────────────────────────────────────────────────────────────────────

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for new user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only profile serializer."""
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'review_count']
        read_only_fields = fields

    def get_review_count(self, obj):
        return obj.reviews.count()
