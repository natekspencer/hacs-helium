"""Helium stats entity."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator import HeliumSolanaDataUpdateCoordinator


@dataclass(kw_only=True)
class HeliumStatSensorEntityDescription(SensorEntityDescription):
    """Helium stat sensor entity description."""

    token: str


def get_stat_sensor_descriptions(
    token: str,
) -> tuple[HeliumStatSensorEntityDescription]:
    """Get stat sensor descriptions from token."""
    return (
        HeliumStatSensorEntityDescription(
            key="total_hotspots",
            name="Total Hotspots",
            icon="mdi:router-wireless",
            token=token,
        ),
        HeliumStatSensorEntityDescription(
            key="active_hotspots",
            name="Active Hotspots",
            icon="mdi:router-wireless",
            token=token,
        ),
        HeliumStatSensorEntityDescription(
            key="total_cities", name="Total Cities", icon="mdi:city", token=token
        ),
        HeliumStatSensorEntityDescription(
            key="total_countries", name="Total Countries", icon="mdi:earth", token=token
        ),
        HeliumStatSensorEntityDescription(
            key="daily_average_rewards",
            name="Daily Average Rewards",
            icon="mdi:hand-coin-outline",
            native_unit_of_measurement=token,
            suggested_display_precision=5,
            token=token,
        ),
    )


class HeliumStats(CoordinatorEntity[HeliumSolanaDataUpdateCoordinator], SensorEntity):
    """Helium stats sensor entity."""

    entity_description: HeliumStatSensorEntityDescription

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: HeliumSolanaDataUpdateCoordinator,
        entity_description: HeliumStatSensorEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description

        token = entity_description.token
        device_id = f"helium.stats.{token}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"Helium Stats {token}",
            manufacturer="Helium",
            model=token,
        )
        self._attr_unique_id = f"{device_id}_{entity_description.key.lower()}"

        self._set_native_value()

    def _set_native_value(self) -> None:
        """Set native value."""
        if data := self.coordinator.data:
            desc = self.entity_description
            self._attr_native_value = data["stats"][desc.token.lower()][desc.key]

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._set_native_value()
        return super()._handle_coordinator_update()
