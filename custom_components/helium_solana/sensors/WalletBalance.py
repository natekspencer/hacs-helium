"""Helium wallet balance sensor entity."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN, TOKEN_SOL
from ..coordinator import HeliumWalletDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class WalletBalance(CoordinatorEntity[HeliumWalletDataUpdateCoordinator], SensorEntity):
    """Helium wallet balance sensor entity for Helium Solana tokens."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:wallet"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self, coordinator: HeliumWalletDataUpdateCoordinator, token: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._token = token if token != TOKEN_SOL else "solana"
        key = token.lower()
        address4 = coordinator.address[:4]

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"helium.wallet.{address4}")},
            name="Helium Wallet " + address4,
            manufacturer="Helium",
        )
        self._attr_name = f"{token} Balance"
        self._attr_native_unit_of_measurement = token
        self._attr_unique_id = f"helium.wallet.{address4}_{key.lower()}"

        self._set_native_value()

    def _set_native_value(self) -> None:
        """Set native value."""
        if data := self.coordinator.data:
            self._attr_native_value = data["balance"][self._token.lower()]

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._set_native_value()
        return super()._handle_coordinator_update()
