import os
import requests

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async

from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.contrib.auth.models import AnonymousUser

from knox.auth import TokenAuthentication

knoxAuth = TokenAuthentication()


@database_sync_to_async
def get_user(token_key):
    try:
        user = knoxAuth.authenticate_credentials(token=token_key)[0]
        return user
    except Exception:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        scope["user"] = AnonymousUser()
        if b"sec-websocket-protocol" in headers:
            scope["user"] = await get_user(headers[b"sec-websocket-protocol"])
        return await self.inner(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))


def get_media_file_path(file_url):
    try:
        if file_url == None or file_url == "":
            return None

        if settings.CI_CD_STAGE == "development":
            media_url = os.environ["BASE_URL"] + settings.MEDIA_URL
            return file_url.split(media_url)[1]
        elif settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
            return file_url.split(settings.AWS_S3_CUSTOM_DOMAIN)[1]
    except Exception:
        # Happens by picture_url.split(settings.AWS_S3_CUSTOM_DOMAIN)[1],
        # because there's the google picture link
        return None


def get_media_file_url(file_path):
    url = ""
    if settings.CI_CD_STAGE == "development":
        url = "{base_url}{path}".format(
            base_url=os.environ["BASE_URL"], path=default_storage.url(file_path)
        )
    elif settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
        url = default_storage.url(file_path)

    url = url.replace("%7B", "{")
    url = url.replace("%7D", "}")

    return url


def now_date():
    return timezone.now().date()


def get_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_country_code(ip):
    r = requests.get("http://www.geoplugin.net/json.gp?ip={}".format(ip))
    if not r.ok:
        return ""
    data = r.json()
    country_code = data["geoplugin_countryCode"]
    return country_code
