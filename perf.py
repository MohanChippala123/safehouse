"""Performance optimizations and caching strategies."""
import time
from functools import wraps
from typing import Callable, Any


def memoize(ttl: int = 300):
    """Memoize function results with TTL."""
    def decorator(func: Callable) -> Callable:
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        wrapper.cache_clear = lambda: cache.clear()
        return wrapper

    return decorator


def batch_requests(batch_size: int = 10, timeout: int = 5):
    """Batch multiple requests for efficiency."""
    def decorator(func: Callable) -> Callable:
        queue = []
        last_flush = time.time()

        @wraps(func)
        def wrapper(item):
            nonlocal last_flush
            queue.append(item)

            now = time.time()
            should_flush = (
                len(queue) >= batch_size or
                (now - last_flush) >= timeout
            )

            if should_flush:
                result = func(queue)
                queue.clear()
                last_flush = now
                return result
            return None

        return wrapper

    return decorator


class ConnectionPool:
    """Reusable connection pool for HTTP requests."""

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pool = []
        self.in_use = set()

    def get(self):
        """Get a connection from pool."""
        import requests
        if self.pool:
            return self.pool.pop()
        if len(self.in_use) < self.max_connections:
            return requests.Session()
        # Wait for connection to be released
        time.sleep(0.1)
        return self.get()

    def release(self, session):
        """Return connection to pool."""
        self.pool.append(session)


def parallel_execution(max_workers: int = 5):
    """Execute function calls in parallel."""
    from concurrent.futures import ThreadPoolExecutor

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(items: list):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return list(executor.map(func, items))
        return wrapper

    return decorator


# Optimization flags
ENABLE_CACHING = True
ENABLE_COMPRESSION = True
ENABLE_LAZY_LOADING = True


def should_cache(response_size: int) -> bool:
    """Decide if response should be cached."""
    return ENABLE_CACHING and response_size < 1024 * 1024  # Cache responses < 1MB
