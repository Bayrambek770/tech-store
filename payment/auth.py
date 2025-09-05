import base64
import binascii

from django.conf import settings
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import get_authorization_header


def authentication(request):
    auth = get_authorization_header(request).split()

    if not auth or auth[0].lower() != b"basic":
        return False

    if len(auth) == 1:
        return False
    elif len(auth) > 2:
        return False

    try:
        auth_parts = (
            base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(":")
        )
    except (TypeError, UnicodeDecodeError, binascii.Error):
        return False

    username, password = auth_parts[0], auth_parts[2]
    return username == settings.PAYLOV_USERNAME and password == settings.PAYLOV_PASSWORD
