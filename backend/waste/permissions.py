from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission, IsAdminUser

from .constants import WORKER_GROUP_NAME
from .models import Device

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class AllowAnyReadOrAdminWrite(BasePermission):
    """
    Allow any user to read (GET, HEAD, OPTIONS),
    but require admin status (is_staff=True) for write operations.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:  # type: ignore
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return IsAdminUser().has_permission(request, view)


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


class IsWorkerOrAdmin(BasePermission):
    """Allow requests from an authenticated worker or a staff user."""

    def has_permission(self, request: Request, view: APIView) -> bool:  # type: ignore
        """Check if the request is from an authenticated worker or a staff user.

        Args:
            request (Request): The incoming request to check permissions for.
            view (APIView): The view that is being accessed.

        Returns:
            bool: True if the request is from an authenticated worker or a staff user, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff
            or request.user.groups.filter(name=WORKER_GROUP_NAME).exists()
        )
