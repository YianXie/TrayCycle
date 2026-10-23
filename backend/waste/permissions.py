from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Device


class IsDeviceOrAdmin(BasePermission):
    """Allow requests from an authenticated camera device or a staff user."""

    def has_permission(self, request: Request, view: APIView) -> bool:  # type: ignore
        """Check if the request is from an authenticated camera device or a staff user.

        Args:
            request (Request): The incoming request to check permissions for.
            view (APIView): The view that is being accessed.

        Returns:
            bool: True if the request is from an authenticated camera device or a staff user, False otherwise.
        """
        if isinstance(request.auth, Device):
            return True
        return request.user and request.user.is_staff
