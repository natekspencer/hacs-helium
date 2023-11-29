"""Helium price sensor entity."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CURRENCY_USD, DOMAIN
from ..coordinator import HeliumPriceDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

TOKEN_ID_MAP = {
    "helium": "HNT",
    "helium-iot": "IOT",
    "helium-mobile": "MOBILE",
    "wrapped-solana": "SOLANA",
}


class PriceSensor(CoordinatorEntity[HeliumPriceDataUpdateCoordinator], SensorEntity):
    """Helium price sensor entity for Helium Solana tokens."""

    _attr_attribution = "Powered by CoinGecko"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 8

    def __init__(
        self, coordinator: HeliumPriceDataUpdateCoordinator, token_id: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._token_id = token_id
        name = TOKEN_ID_MAP[token_id]

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "helium.price")},
            name="Helium Price",
            manufacturer="Helium",
        )
        self._attr_name = name
        self._attr_unique_id = f"helium.price.{name.lower()}"

        self._set_native_value()

    def _set_native_value(self) -> None:
        """Set native value."""
        if (data := self.coordinator.data) and (data := data[self._token_id]):
            currency = self.coordinator.hass.config.currency
            if (value := data[currency.lower()]) is None:
                currency = CURRENCY_USD
                value = data[currency.lower()]
            self._attr_native_unit_of_measurement = currency
            self._attr_native_value = value

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._set_native_value()
        return super()._handle_coordinator_update()
