import time

class Cache:
    def __init__(self, default_expiration=None):
        self.cache = {}
        self.default_expiration = default_expiration

    def set(self, key, value, expiration=None):
        """
        Store a value in the cache with an optional expiration time (in seconds).
        If expiration is not provided, the default expiration time will be used.
        """
        if expiration is None:
            expiration = self.default_expiration

        if expiration:
            expiration_time = time.time() + expiration
            self.cache[key] = (value, expiration_time)
        else:
            self.cache[key] = (value, None)

    def get(self, key):
        """
        Retrieve a value from the cache. If the value has expired, return None.
        """
        value, expiration_time = self.cache.get(key, (None, None))
        if expiration_time and time.time() > expiration_time:
            self.delete(key)
            return None
        return value

    def delete(self, key):
        """
        Remove a key-value pair from the cache.
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clear the entire cache.
        """
        self.cache = {}