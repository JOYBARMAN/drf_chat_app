from django.core.cache import cache
from django.db.models.manager import Manager

from shared.cache_key import get_model_cache_key


class CacheModelManager(Manager):
    def get_queryset(self):
        """Get the queryset from the cache if it exists, otherwise get it from the database."""
        self.cache_key = get_model_cache_key(model_name=self.model.__name__)
        # Get the queryset from the cache
        queryset = cache.get(self.cache_key)
        # If the queryset is not in the cache, get it from the database and set it in the cache
        if queryset is None:
            queryset = super().get_queryset()
            cache.set(self.cache_key, queryset)

        return queryset

    def get(self, *args, **kwargs):
        """Get the object from the cache if it exists, otherwise get it from the database."""
        return super().get(*args, **kwargs)

    def create(self, **kwargs):
        """Create the object and update the cache."""
        instance = super().create(**kwargs)

        # Update the cache
        self.update_cache()

        return instance

    def update_cache(self):
        """Update the cache with the queryset."""
        self.clear_cache()
        return self.get_queryset()

    def clear_cache(self):
        """Clear the cache."""
        return cache.delete(self.cache_key)
