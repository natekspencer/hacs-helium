"""Helium solana data coordinator."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from requests.exceptions import RequestException

from .api.backend import BackendAPI
from .const import COINGECKO_PRICE_URL, CURRENCY_USD, DOMAIN
from .utility import http_client

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=10)

TOKEN_IDS = ("helium", "helium-iot", "helium-mobile", "wrapped-solana")


class HeliumSolanaDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: BackendAPI) -> None:
        """Initialize."""
        self.api = api
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    async def _async_update_data(self) -> dict | None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Requesting Helium stats data")
        try:
            response = await self.api.get_data("heliumstats")
            if response.status_code == 200:
                return response.json()
        except RequestException as ex:
            _LOGGER.exception("Error retrieving helium stats from hotspotty")
            raise UpdateFailed(ex) from ex


class HeliumPriceDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, dict[str, float]]]
):
    """Helium price data update coordinator."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    async def _async_update_data(self) -> dict | None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Requesting token prices from CoinGecko")
        currencies = set((self.hass.config.currency, CURRENCY_USD))
        try:
            response = await asyncio.to_thread(
                http_client,
                f"{COINGECKO_PRICE_URL}?ids={','.join(TOKEN_IDS)}&vs_currencies={','.join(currencies)}",
            )
            if response.status_code == 200:
                return response.json()
        except RequestException as ex:
            _LOGGER.exception("Error retrieving token prices from CoinGecko")
            raise UpdateFailed(ex) from ex
