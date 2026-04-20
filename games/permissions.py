from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Allow unrestricted read access (GET, HEAD, OPTIONS) to any request.
    Write access (POST, PUT, PATCH, DELETE) is restricted to staff users only.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
