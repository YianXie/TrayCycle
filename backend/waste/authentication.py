from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions
from rest_framework.request import Request

from .models import Device


class DeviceTokenAuthentication(authentication.BaseAuthentication):
    """Authenticate camera devices via an 'Authorization: Device <token>' header."""

    keyword = "Device"

    def authenticate(self, request: Request) -> tuple[AnonymousUser, Device] | None:
        """Authenticate the request and return a tuple of (user, device) if successful.

        Args:
            request (Request): The incoming request to authenticate.

        Raises:
            exceptions.AuthenticationFailed: If the authentication fails due to an invalid token or header format.

        Returns:
            tuple[AnonymousUser, Device] | None: A tuple containing an AnonymousUser and the authenticated Device if successful, or None if the request is not a device request.
        """
        parts = authentication.get_authorization_header(request).split()
        if not parts or parts[0].decode().lower() != self.keyword.lower():
            return None  # not a device request
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Invalid Device header.")

        try:
            token = parts[1].decode()
        except UnicodeDecodeError as e:
            raise exceptions.AuthenticationFailed("Invalid token encoding.") from e

        device = Device.objects.filter(token=token).first()
        if device is None:
            raise exceptions.AuthenticationFailed("Invalid device token.")
        return (AnonymousUser(), device)

    def authenticate_header(self, request: Request) -> str:  # type: ignore
        """Return the value for the 'WWW-Authenticate' header in case of an authentication failure.

        Args:
            request (Request): The incoming request that failed authentication.

        Returns:
            str: The value for the 'WWW-Authenticate' header, indicating the authentication scheme and realm.
        """
        return self.keyword
