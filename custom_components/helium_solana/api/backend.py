"""Backend API."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import requests

from ..const import BACKEND_KEY, BACKEND_URL

_LOGGER = logging.getLogger(__name__)


class BackendAPI:
    def __init__(self, cache_ttl: int = 600):
        self._cache: dict[str, Any] = {}
        self._cache_ttl = cache_ttl

    @staticmethod
    def http_client(
        path: str,
        payload: Any | None = None,
        method: str = "GET",
        headers: Any | None = None,
    ) -> requests.Response:
        """Make the HTTP request with the given URL, payload, method, and headers."""
        response = requests.request(
            method, BACKEND_URL + "/" + path, json=payload, headers=headers
        )
        response.raise_for_status()
        return response

    async def get_data(
        self, path: str, cache_key: str | None = None
    ) -> requests.Response:
        """Get the data from a path."""
        cache_key = cache_key or path  # use path as cache key if cache key not provided
        now = time.time()
        cache_entry = self._cache.get(cache_key)
        if cache_entry is None or now - cache_entry["time"] > self._cache_ttl:
            _LOGGER.debug("Refreshing data from %s", path)
            headers = {"Authorization": "bearer " + BACKEND_KEY}
            response = await asyncio.to_thread(
                self.http_client, path, None, "GET", headers
            )
            self._cache[cache_key] = {"data": response, "time": now}

        return self._cache[cache_key]["data"]
