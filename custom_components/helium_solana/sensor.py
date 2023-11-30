"""Helium Solana Integration"""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant import config_entries, core
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.backend import BackendAPI
from .const import (
    ADDRESS_HNT,
    ADDRESS_IOT,
    ADDRESS_MOBILE,
    ADDRESS_SOLANA,
    CONF_INTEGRATION,
    CONF_WALLET,
    DOMAIN,
    INTEGRATION_GENERAL_STATS,
    INTEGRATION_GENERAL_TOKEN_PRICE,
    INTEGRATION_WALLET,
    TOKEN_HELIUM,
    TOKEN_IOT,
    TOKEN_MOBILE,
    TOKEN_SOL,
)
from .coordinator import (
    TOKEN_IDS,
    HeliumHotspotDataUpdateCoordinator,
    HeliumPriceDataUpdateCoordinator,
    HeliumStatsDataUpdateCoordinator,
    HeliumWalletDataUpdateCoordinator,
)
from .sensors.HeliumStats import HeliumStats, get_stat_sensor_descriptions
from .sensors.HotspotReward import HotspotReward
from .sensors.PriceSensor import PriceSensor
from .sensors.StakingRewardsPosition import StakingRewardsPosition
from .sensors.StakingRewardsToken import StakingRewardsToken
from .sensors.WalletBalance import WalletBalance
from .utility import http_client

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)


api_backend = BackendAPI()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup Helium Solana sensors from a config entry."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    integration = config.get(CONF_INTEGRATION)
    wallet = config.get(CONF_WALLET)
    sensors = await get_sensors(integration, wallet, hass)
    async_add_entities(sensors, update_before_add=True)


async def get_sensors(integration: str, wallet: str, hass: HomeAssistant):
    """Get sensors."""
    if integration == INTEGRATION_GENERAL_STATS:
        coordinator = HeliumStatsDataUpdateCoordinator(hass, api_backend)
        await coordinator.async_config_entry_first_refresh()

        return (
            HeliumStats(coordinator, description)
            for token in (TOKEN_IOT, TOKEN_MOBILE)
            for description in get_stat_sensor_descriptions(token)
        )

    if integration == INTEGRATION_GENERAL_TOKEN_PRICE:
        coordinator = HeliumPriceDataUpdateCoordinator(hass)
        await coordinator.async_config_entry_first_refresh()

        return (PriceSensor(coordinator, token_id) for token_id in TOKEN_IDS)

    sensors = []

    if integration == INTEGRATION_WALLET:
        coordinator = HeliumWalletDataUpdateCoordinator(hass, api_backend, wallet)
        await coordinator.async_config_entry_first_refresh()

        sensors.extend(
            WalletBalance(coordinator, token)
            for token in (TOKEN_HELIUM, TOKEN_IOT, TOKEN_MOBILE, TOKEN_SOL)
        )

        coordinator = HeliumHotspotDataUpdateCoordinator(hass, api_backend, wallet)
        await coordinator.async_config_entry_first_refresh()

        if rewards := coordinator.data:
            sensors.extend(
                HotspotReward(
                    coordinator,
                    rewards["rewards"][hotspot_index]["name"],
                    ["rewards", hotspot_index, f"{reward_type}_rewards"],
                    f"{reward_type.title()} Rewards",
                    rewards["rewards"][hotspot_index]["token"],
                )
                for hotspot_index in rewards["rewards"]
                for reward_type in ("claimed", "unclaimed", "total")
            )
            sensors.extend(
                HotspotReward(
                    coordinator,
                    wallet,
                    ["rewards_aggregated", token, f"{reward_type}_rewards"],
                    f"{reward_type.title()} Rewards",
                    token,
                )
                for token in rewards["rewards_aggregated"]
                for reward_type in ("claimed", "unclaimed", "total")
            )

        response = None
        try:
            response = await api_backend.get_data("staking-rewards/" + str(wallet))
        except:
            _LOGGER.exception("No staking rewards found")

        if response.status_code == 200:
            rewards = response.json()
            for delegated_position_key in rewards["rewards"]:
                sensors.append(
                    StakingRewardsPosition(
                        api_backend,
                        wallet,
                        delegated_position_key,
                        rewards["rewards"][delegated_position_key],
                        "mdi:hand-coin-outline",
                    )
                )
                # pass

            for token in rewards["rewards_aggregated"]:
                sensors.append(
                    StakingRewardsToken(
                        api_backend, wallet, token, "mdi:hand-coin-outline"
                    )
                )
                # pass

    return sensors
