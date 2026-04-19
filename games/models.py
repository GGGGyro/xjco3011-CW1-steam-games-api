"""Data models for the Steam Games API."""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Game(models.Model):
    """
    Represents a game available on the Steam platform.

    Fields are aligned with the Kaggle 'Steam Store Games (Clean dataset)' schema
    (https://www.kaggle.com/datasets/nikdavis/steam-store-games), with additional
    computed/derived fields for richer analytics.
    """

    appid = models.IntegerField(
        unique=True,
        help_text="Steam application ID (unique identifier from Steam Store)."
    )
    name = models.CharField(
        max_length=255,
        help_text="Title of the game."
    )
    release_date = models.DateField(
        null=True, blank=True,
        help_text="Official release date on Steam (YYYY-MM-DD)."
    )
    developer = models.CharField(
        max_length=255, blank=True, default='',
        help_text="Developer name(s); semicolon-delimited if multiple."
    )
    publisher = models.CharField(
        max_length=255, blank=True, default='',
        help_text="Publisher name(s); semicolon-delimited if multiple."
    )
    platforms = models.CharField(
        max_length=100, blank=True, default='',
        help_text="Supported platforms (e.g. 'windows;mac;linux')."
    )
    required_age = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(21)],
        help_text="Minimum required age (PEGI standard); 0 means unrated."
    )
    english = models.BooleanField(
        default=True,
        help_text="Whether the game supports English."
    )
    categories = models.TextField(
        blank=True, default='',
        help_text="Semicolon-delimited Steam categories."
    )
    genres = models.TextField(
        blank=True, default='',
        help_text="Semicolon-delimited Steam genres (e.g. 'Action;RPG')."
    )
    steamspy_tags = models.TextField(
        blank=True, default='',
        help_text="Semicolon-delimited SteamSpy community tags."
    )
    achievements = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total number of Steam achievements available."
    )
    positive_ratings = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of positive user ratings (from SteamSpy)."
    )
    negative_ratings = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of negative user ratings (from SteamSpy)."
    )
    average_playtime = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Average playtime in minutes (from SteamSpy)."
    )
    median_playtime = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Median playtime in minutes (from SteamSpy)."
    )
    owners = models.CharField(
        max_length=50, blank=True, default='',
        help_text="Estimated ownership range (e.g. '10000000-20000000')."
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Current price in USD; 0.00 indicates a free-to-play title."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'games'
        ordering = ['-positive_ratings']
        indexes = [
            models.Index(fields=['appid']),
            models.Index(fields=['name']),
            models.Index(fields=['release_date']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.name} (AppID: {self.appid})"

    @property
    def total_ratings(self):
        return self.positive_ratings + self.negative_ratings

    @property
    def approval_rate(self):
        total = self.total_ratings
        if total == 0:
            return None
        return round((self.positive_ratings / total) * 100, 2)

    @property
    def is_free(self):
        return self.price == 0

    @property
    def genre_list(self):
        return [g.strip() for g in self.genres.split(';') if g.strip()]

    @property
    def platform_list(self):
        return [p.strip() for p in self.platforms.split(';') if p.strip()]


class Review(models.Model):
    """
    Represents a user-submitted review for a Steam game.
    A user may submit at most one review per game.
    """

    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The game being reviewed."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The user who submitted this review."
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Numeric rating from 1 (worst) to 10 (best)."
    )
    title = models.CharField(
        max_length=200,
        help_text="Short title or headline for the review."
    )
    body = models.TextField(
        help_text="Full review text."
    )
    hours_played = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Hours the reviewer has played this game (optional)."
    )
    recommended = models.BooleanField(
        default=True,
        help_text="Whether the reviewer recommends this game."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('game', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['game', 'rating']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Review by {self.user.username} on {self.game.name} ({self.rating}/10)"
