from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Turn ProtectedError into a 409 instead of a 500.

    Args:
        exc (Exception): The raised exception.
        context (dict): DRF view context.

    Returns:
        Response | None: A 409 response for ProtectedError, otherwise DRF's default handling.
    """
    if isinstance(exc, ProtectedError):
        return Response(
            {"detail": "This object is still referenced and cannot be deleted."},
            status=status.HTTP_409_CONFLICT,
        )
    return exception_handler(exc, context)
