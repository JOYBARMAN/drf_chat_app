from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.conf import settings


class CachedQuerysetMixin:
    """
    Mixin that provides caching for querysets in Django views.
    """

    cache_timeout = 600

    def get_cache_key(self):
        """
        Generate a unique cache key
        """
        return f"{self.__class__.__name__}_queryset"

    def get_cache_timeout(self):
        """
        Return the cache timeout.
        You can override this method to provide dynamic timeouts if needed.
        """
        return getattr(settings, "DEFAULT_CACHE_TIMEOUT", self.cache_timeout)

    def get_queryset(self):
        """
        Retrieve the queryset from the cache or fetch from the database if not cached.
        """
        cache_key = self.get_cache_key()
        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            # Fetch the queryset from the database and cache it
            queryset = self.fetch_queryset()
            cache.set(cache_key, queryset, timeout=self.get_cache_timeout())
            return queryset

        return cached_queryset

    def fetch_queryset(self):
        """
        This method should be overridden in the view or subclass
        to provide the actual queryset.
        """
        raise NotImplementedError("You must implement the `fetch_queryset` method.")

    def perform_create(self, serializer):
        """
        Override this method to handle cache invalidation when a new instance is created.
        """
        # Save the new instance
        instance = serializer.save()

        # Invalidate the cache after creating the new instance
        cache_key = self.get_cache_key()
        cache.delete(cache_key)

        return instance

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)



class CacheMethod:
    def clear_cache(self, cache_key):
        cache.delete(cache_key)