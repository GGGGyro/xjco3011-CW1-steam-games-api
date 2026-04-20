"""Views for the Steam Games API."""

from django.db.models import (
    Avg, Count, Sum, Max, Min, F, Q,
    FloatField, ExpressionWrapper
)
from django.db.models.functions import TruncYear, TruncMonth
from django.contrib.auth.models import User

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import Game, Review
from .serializers import (
    GameListSerializer, GameDetailSerializer,
    ReviewSerializer,
    UserRegistrationSerializer, UserProfileSerializer,
)
from .filters import GameFilter
from .utils import paginated_response


@extend_schema_view(
    list=extend_schema(summary="List all games", tags=["games"]),
    create=extend_schema(summary="Create a new game", tags=["games"]),
    retrieve=extend_schema(summary="Retrieve a game by ID", tags=["games"]),
    update=extend_schema(summary="Update a game (full)", tags=["games"]),
    partial_update=extend_schema(summary="Update a game (partial)", tags=["games"]),
    destroy=extend_schema(summary="Delete a game", tags=["games"]),
)
class GameViewSet(viewsets.ModelViewSet):
    """CRUD + analytics for Steam game records."""

    queryset = Game.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = GameFilter
    search_fields = ['name', 'developer', 'publisher', 'genres', 'steamspy_tags']
    ordering_fields = ['name', 'release_date', 'price', 'positive_ratings', 'negative_ratings', 'average_playtime']
    ordering = ['-positive_ratings']

    def get_serializer_class(self):
        if self.action == 'list':
            return GameListSerializer
        return GameDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        return Response(
            {"success": True, "message": "Game created successfully.", "data": GameDetailSerializer(game).data},
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        return Response({"success": True, "message": "Game updated successfully.", "data": GameDetailSerializer(game).data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name
        instance.delete()
        return Response({"success": True, "message": f"Game '{name}' deleted successfully."}, status=status.HTTP_200_OK)

    @extend_schema(summary="Overall dataset statistics", tags=["analytics"])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def stats(self, request):
        qs = Game.objects.all()
        total = qs.count()
        free_count = qs.filter(price=0).count()
        agg = qs.aggregate(
            avg_price=Avg('price'), max_price=Max('price'),
            total_positive=Sum('positive_ratings'), total_negative=Sum('negative_ratings'),
            avg_positive=Avg('positive_ratings'), avg_playtime=Avg('average_playtime'),
            max_achievements=Max('achievements'),
        )
        data = {
            "total_games": total, "free_to_play": free_count, "paid": total - free_count,
            "price": {"average_usd": round(float(agg['avg_price'] or 0), 2), "max_usd": float(agg['max_price'] or 0)},
            "ratings": {"total_positive": agg['total_positive'] or 0, "total_negative": agg['total_negative'] or 0,
                        "avg_positive_per_game": round(float(agg['avg_positive'] or 0), 1)},
            "playtime": {"avg_minutes": round(float(agg['avg_playtime'] or 0), 1),
                         "avg_hours": round(float(agg['avg_playtime'] or 0) / 60, 2)},
            "max_achievements": agg['max_achievements'] or 0,
        }
        return Response(paginated_response(data, "Dataset statistics retrieved successfully."))

    @extend_schema(summary="Genre distribution breakdown", tags=["analytics"])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def genre_breakdown(self, request):
        games = Game.objects.values_list('genres', flat=True)
        counts = {}
        for genre_str in games:
            for genre in genre_str.split(';'):
                genre = genre.strip()
                if genre:
                    counts[genre] = counts.get(genre, 0) + 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        data = [{"genre": g, "count": c} for g, c in sorted_counts]
        return Response(paginated_response(data, "Genre breakdown retrieved.", {"total_genres": len(data)}))

    @extend_schema(summary="Top-rated games by approval rate", tags=["analytics"],
        parameters=[OpenApiParameter('limit', OpenApiTypes.INT), OpenApiParameter('min_ratings', OpenApiTypes.INT)])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def top_rated(self, request):
        limit = min(int(request.query_params.get('limit', 10)), 50)
        min_ratings = int(request.query_params.get('min_ratings', 1000))
        games = (
            Game.objects
            .annotate(total=F('positive_ratings') + F('negative_ratings'))
            .filter(total__gte=min_ratings)
            .annotate(approval=ExpressionWrapper(
                F('positive_ratings') * 100.0 / (F('positive_ratings') + F('negative_ratings')),
                output_field=FloatField()))
            .order_by('-approval')[:limit]
        )
        data = [{"rank": idx+1, "id": g.id, "appid": g.appid, "name": g.name, "developer": g.developer,
                 "genres": g.genres, "price": float(g.price), "positive_ratings": g.positive_ratings,
                 "negative_ratings": g.negative_ratings, "total_ratings": g.total,
                 "approval_rate": round(g.approval, 2)} for idx, g in enumerate(games)]
        return Response(paginated_response(data, f"Top {limit} rated games retrieved.", {"count": len(data)}))

    @extend_schema(summary="Game release trend over time", tags=["analytics"],
        parameters=[OpenApiParameter('granularity', OpenApiTypes.STR)])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def release_trend(self, request):
        granularity = request.query_params.get('granularity', 'year')
        trunc = TruncMonth if granularity == 'month' else TruncYear
        fmt = '%Y-%m' if granularity == 'month' else '%Y'
        qs = (Game.objects.filter(release_date__isnull=False)
              .annotate(period=trunc('release_date'))
              .values('period').annotate(count=Count('id')).order_by('period'))
        data = [{"period": item['period'].strftime(fmt), "count": item['count']} for item in qs]
        return Response(paginated_response(data, f"Release trend by {granularity} retrieved.", {"granularity": granularity}))

    @extend_schema(summary="Price range distribution", tags=["analytics"])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def price_distribution(self, request):
        buckets = [
            ("Free", Q(price=0)), ("$0.01-$4.99", Q(price__gt=0, price__lte=4.99)),
            ("$5-$9.99", Q(price__gte=5, price__lte=9.99)), ("$10-$19.99", Q(price__gte=10, price__lte=19.99)),
            ("$20-$29.99", Q(price__gte=20, price__lte=29.99)), ("$30-$39.99", Q(price__gte=30, price__lte=39.99)),
            ("$40-$59.99", Q(price__gte=40, price__lte=59.99)), ("$60+", Q(price__gte=60)),
        ]
        data = [{"bucket": label, "count": Game.objects.filter(q).count()} for label, q in buckets]
        return Response(paginated_response(data, "Price distribution retrieved."))

    @extend_schema(summary="Platform support statistics", tags=["analytics"])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def platform_stats(self, request):
        total = Game.objects.count()
        data = {
            "total_games": total,
            "windows": Game.objects.filter(platforms__icontains='windows').count(),
            "mac": Game.objects.filter(platforms__icontains='mac').count(),
            "linux": Game.objects.filter(platforms__icontains='linux').count(),
            "all_platforms": Game.objects.filter(platforms__icontains='windows').filter(
                platforms__icontains='mac').filter(platforms__icontains='linux').count(),
        }
        return Response(paginated_response(data, "Platform statistics retrieved."))

    @extend_schema(summary="Developer leaderboard by total positive ratings", tags=["analytics"],
        parameters=[OpenApiParameter('limit', OpenApiTypes.INT)])
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def developer_leaderboard(self, request):
        limit = min(int(request.query_params.get('limit', 10)), 50)
        qs = (Game.objects.values('developer')
              .annotate(game_count=Count('id'), total_positive=Sum('positive_ratings'), avg_price=Avg('price'))
              .order_by('-total_positive')[:limit])
        data = [{"rank": idx+1, "developer": item['developer'], "game_count": item['game_count'],
                 "total_positive_ratings": item['total_positive'],
                 "avg_price_usd": round(float(item['avg_price'] or 0), 2)} for idx, item in enumerate(qs)]
        return Response(paginated_response(data, f"Top {limit} developers retrieved.", {"count": len(data)}))

    @extend_schema(summary="Find similar games by genre", tags=["analytics"],
        parameters=[OpenApiParameter('limit', OpenApiTypes.INT)])
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def similar(self, request, pk=None):
        game = self.get_object()
        limit = min(int(request.query_params.get('limit', 5)), 20)
        genre_filters = Q()
        for genre in game.genre_list:
            genre_filters |= Q(genres__icontains=genre)
        similar_games = Game.objects.filter(genre_filters).exclude(pk=game.pk).order_by('-positive_ratings')[:limit]
        data = GameListSerializer(similar_games, many=True).data
        return Response(paginated_response(data, f"Games similar to '{game.name}' retrieved.",
                                           {"source_game": game.name, "count": len(data)}))


@extend_schema_view(
    list=extend_schema(summary="List all reviews", tags=["reviews"]),
    create=extend_schema(summary="Create a new review", tags=["reviews"]),
    retrieve=extend_schema(summary="Retrieve a review by ID", tags=["reviews"]),
    update=extend_schema(summary="Update a review (full)", tags=["reviews"]),
    partial_update=extend_schema(summary="Update a review (partial)", tags=["reviews"]),
    destroy=extend_schema(summary="Delete a review", tags=["reviews"]),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD endpoint for user reviews."""

    queryset = Review.objects.select_related('game', 'user').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['game', 'recommended']
    search_fields = ['title', 'body', 'user__username', 'game__name']
    ordering_fields = ['rating', 'created_at', 'hours_played']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        game_id = self.request.query_params.get('game_id')
        if game_id:
            qs = qs.filter(game_id=game_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"success": False, "error": {"code": 403, "message": "You can only edit your own reviews."}},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"success": False, "error": {"code": 403, "message": "You can only delete your own reviews."}},
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({"success": True, "message": "Review deleted."}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/ - Register a new user."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(summary="Register a new user", tags=["auth"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"success": True, "message": "User registered successfully.",
                         "data": UserProfileSerializer(user).data}, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveAPIView):
    """GET /api/v1/auth/profile/ - Returns the authenticated user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get current user profile", tags=["auth"])
    def get_object(self):
        return self.request.user
