"""URL routing for the games application."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import GameViewSet, ReviewViewSet, RegisterView, ProfileView

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # ── CRUD + Analytics ──────────────────────────────────────────────────────
    path('', include(router.urls)),

    # ── Authentication ────────────────────────────────────────────────────────
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/profile/', ProfileView.as_view(), name='auth-profile'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token-verify'),
]
