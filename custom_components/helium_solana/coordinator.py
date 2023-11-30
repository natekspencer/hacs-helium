"""Helium solana data coordinator."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from requests.exceptions import RequestException

from .api.backend import BackendAPI
from .const import COINGECKO_PRICE_URL, CURRENCY_USD
from .utility import http_client

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=10)

TOKEN_IDS = ("helium", "helium-iot", "helium-mobile", "wrapped-solana")


class HeliumStatsDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Helium stats data update coordinator."""

    def __init__(self, hass: HomeAssistant, api: BackendAPI) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass, _LOGGER, name="Helium stats", update_interval=UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> dict | None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Requesting Helium stats data")
        try:
            response = await self.api.get_data("heliumstats")
            if response.status_code == 200:
                return response.json()
        except RequestException as ex:
            _LOGGER.exception("Error retrieving helium stats")
            raise UpdateFailed(ex) from ex


class HeliumPriceDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, dict[str, float]]]
):
    """Helium price data update coordinator."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(
            hass, _LOGGER, name="Helium price", update_interval=UPDATE_INTERVAL
        )

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


class HeliumWalletDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Helium wallet data update coordinator."""

    def __init__(self, hass: HomeAssistant, api: BackendAPI, address: str) -> None:
        """Initialize."""
        self.api = api
        self.address = address
        super().__init__(
            hass, _LOGGER, name="Helium wallet", update_interval=UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> dict | None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Requesting Helium stats data")
        try:
            response = await self.api.get_data(f"wallet/{self.address}")
            if response.status_code == 200:
                return response.json()
        except RequestException as ex:
            _LOGGER.exception("Error retrieving helium wallet balances")
            raise UpdateFailed(ex) from ex


class HeliumHotspotDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Helium hotspot data update coordinator."""

    def __init__(self, hass: HomeAssistant, api: BackendAPI, address: str) -> None:
        """Initialize."""
        self.api = api
        self.address = address
        super().__init__(
            hass, _LOGGER, name="Helium hotspot", update_interval=UPDATE_INTERVAL
        )

    async def _async_update_data(self) -> dict | None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Requesting Helium stats data")
        try:
            response = await self.api.get_data(f"hotspot-rewards2/{self.address}")
            if response.status_code == 200:
                return response.json()
        except RequestException as ex:
            _LOGGER.exception("Error retrieving helium hotspot rewards")
            raise UpdateFailed(ex) from ex
