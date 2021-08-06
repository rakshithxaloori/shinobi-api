from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async

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
