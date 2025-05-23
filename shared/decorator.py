from functools import wraps

from shared.services import CacheMethod


def cache_results(get_cache_key):
    """
    Decorator to cache the result of a method using a generated cache key.

    :param get_cache_key: A callable that accepts the same arguments as the wrapped function
    and returns a cache key.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate the cache key
            cache_key = get_cache_key(*args, **kwargs)
            cache = CacheMethod()

            # Try to get data from cache
            cached_data = cache.get_cache_data(cache_key=cache_key)
            if cached_data is not None:
                return cached_data

            # Call the original function
            results = func(*args, **kwargs)

            # Store the result in cache
            cache.set_cache_data(cache_key=cache_key, data=results)
            return results

        return wrapper

    return decorator
