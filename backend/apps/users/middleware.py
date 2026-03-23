import os
from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model

# Get user model from Django settings
User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        close_old_connections()
        
        # Pull token from query string
        query_string = scope.get("query_string", b"").decode()
        token = None
        
        if "token=" in query_string:
            token = query_string.split("token=")[1].split("&")[0]

        if token:
            try:
                # Validate token
                UntypedToken(token)
                
                # Decode to get user_id
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get("user_id")
                
                scopetasks = []
                scope["user"] = await get_user(user_id)
            except (InvalidToken, TokenError, Exception) as e:
                print(f"WS Auth Error: {e}")
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)
