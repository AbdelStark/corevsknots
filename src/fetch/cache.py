"""
Cache manager for API responses.

This module provides a simple caching mechanism for API responses to reduce
the number of API calls and improve performance.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class Cache:
    """
    Simple file-based cache for API responses.
    """

    def __init__(self, cache_dir: str = "./.cache", expiry_hours: int = 24):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            expiry_hours: Cache expiry time in hours
        """
        self.cache_dir = cache_dir
        self.expiry_seconds = expiry_hours * 3600

        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_key(self, key: str) -> str:
        """
        Generate a cache key.

        Args:
            key: Original key

        Returns:
            MD5 hash of the key
        """
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> str:
        """
        Get the path to the cache file.

        Args:
            key: Cache key

        Returns:
            Path to the cache file
        """
        hashed_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{hashed_key}.json")

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)

            # Check if cache is expired
            if time.time() - cache_data["timestamp"] > self.expiry_seconds:
                logger.debug(f"Cache expired for {key}")
                return None

            logger.debug(f"Cache hit for {key}")
            return cache_data["data"]

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Invalid cache file {cache_path}: {e}")
            return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)

        cache_data = {"timestamp": time.time(), "data": value}

        try:
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            logger.debug(f"Cached data for {key}")

        except (IOError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to cache data for {key}: {e}")

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache.

        Args:
            key: Cache key to clear (if None, clear all cache)
        """
        if key:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.debug(f"Cleared cache for {key}")
        else:
            # Clear all cache files
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, filename))

            logger.debug("Cleared all cache")

    def clear_expired(self) -> None:
        """
        Clear expired cache entries.
        """
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.cache_dir, filename)

                try:
                    with open(file_path, "r") as f:
                        cache_data = json.load(f)

                    # Check if cache is expired
                    if time.time() - cache_data["timestamp"] > self.expiry_seconds:
                        os.remove(file_path)
                        count += 1

                except (json.JSONDecodeError, KeyError, IOError) as e:
                    logger.warning(f"Invalid cache file {file_path}: {e}")
                    # Remove invalid cache file
                    os.remove(file_path)
                    count += 1

        logger.debug(f"Cleared {count} expired cache entries")
