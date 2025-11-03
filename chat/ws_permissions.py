class BasePermission:
    """Base permission structure."""

    async def has_permission(self, scope, consumer=None):
        return True


class IsAuthenticatedPermission(BasePermission):
    async def has_permission(self, scope, consumer=None):
        return True
        # user = scope.get("user")
        # return user and user.is_authenticated


class DummyPermission(BasePermission):
    async def has_permission(self, scope, consumer=None):
        return False
