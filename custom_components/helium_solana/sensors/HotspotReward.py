"""Hotspot reward sensor entity."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator import HeliumHotspotDataUpdateCoordinator
from ..utility import title_case_and_replace_hyphens

_LOGGER = logging.getLogger(__name__)


class HotspotReward(
    CoordinatorEntity[HeliumHotspotDataUpdateCoordinator], SensorEntity
):
    """Hotspot reward sensor entity."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:hand-coin-outline"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator: HeliumHotspotDataUpdateCoordinator,
        identifier: str,
        path: list[str],
        name: str,
        token: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self.path = path

        if path[0] == "rewards_aggregated":
            device_id = f"helium.wallet.rewards.{identifier[:4]}"
            device_name = f"Helium Hotspot Reward Wallet {identifier[:4]}"
        else:
            title = title_case_and_replace_hyphens(identifier)
            device_id = f"helium.hotspot.rewards.{identifier}"
            device_name = f"Helium Hotspot {title}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Helium",
        )
        self._attr_name = name
        self._attr_native_unit_of_measurement = token.upper()
        self._attr_unique_id = f"helium.hotspot-reward.{coordinator.address[:4]}_{path[0]}_{path[1]}_{path[2]}"

        self._set_native_value()

    def _set_native_value(self) -> None:
        """Set native value."""
        if data := self.coordinator.data:
            self._attr_native_value = (
                data[self.path[0]][self.path[1]][self.path[2]] / 10**6
            )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._set_native_value()
        return super()._handle_coordinator_update()
