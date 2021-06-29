from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async

from django.contrib.auth.models import AnonymousUser


from knox.models import AuthToken


@database_sync_to_async
def get_user(headers):
    try:
        token_name, token_key = headers[b"authorization"].decode().split()
        if token_name == "Token":
            token = AuthToken.objects.get(token_key=token_key)
            return token.user
    except AuthToken.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        if b"authorization" in headers:
            scope["user"] = await get_user(headers)
        return await self.inner(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
