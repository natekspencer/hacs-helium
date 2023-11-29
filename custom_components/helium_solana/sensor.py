"""Helium Solana Integration"""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant import config_entries, core

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
    TOKEN_IOT,
    TOKEN_MOBILE,
)
from .coordinator import (
    TOKEN_IDS,
    HeliumPriceDataUpdateCoordinator,
    HeliumSolanaDataUpdateCoordinator,
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
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup Helium Solana sensors from a config entry."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    integration = config.get(CONF_INTEGRATION)
    wallet = config.get(CONF_WALLET)
    sensors = await get_sensors(integration, wallet, hass)
    async_add_entities(sensors, update_before_add=True)


async def get_sensors(integration, wallet, hass):
    """Get sensors."""
    if integration == INTEGRATION_GENERAL_STATS:
        coordinator = HeliumSolanaDataUpdateCoordinator(hass, api_backend)
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
        sensors.append(
            WalletBalance(
                api_backend, wallet, "hnt", ["balance", "hnt"], "HNT", "mdi:wallet"
            )
        )
        sensors.append(
            WalletBalance(
                api_backend, wallet, "iot", ["balance", "iot"], "IOT", "mdi:wallet"
            )
        )
        sensors.append(
            WalletBalance(
                api_backend, wallet, "sol", ["balance", "solana"], "SOL", "mdi:wallet"
            )
        )
        sensors.append(
            WalletBalance(
                api_backend,
                wallet,
                "mobile",
                ["balance", "mobile"],
                "MOBILE",
                "mdi:wallet",
            )
        )
        response = None
        try:
            response = await api_backend.get_data("hotspot-rewards2/" + str(wallet))
        except:
            _LOGGER.exception("No hotspot rewards found")

        if response and response.status_code == 200:
            rewards = response.json()
            # hotspots = len(rewards.rewards)
            for hotspot_index in rewards["rewards"]:
                hotspot_name = rewards["rewards"][hotspot_index]["name"]
                hotspot_token = rewards["rewards"][hotspot_index]["token"]
                sensors.append(
                    HotspotReward(
                        api_backend,
                        wallet,
                        hotspot_name,
                        ["rewards", hotspot_index, "claimed_rewards"],
                        "Claimed Rewards",
                        hotspot_token,
                        "mdi:hand-coin-outline",
                    )
                )
                sensors.append(
                    HotspotReward(
                        api_backend,
                        wallet,
                        hotspot_name,
                        ["rewards", hotspot_index, "unclaimed_rewards"],
                        "Unclaimed Rewards",
                        hotspot_token,
                        "mdi:hand-coin-outline",
                    )
                )
                sensors.append(
                    HotspotReward(
                        api_backend,
                        wallet,
                        hotspot_name,
                        ["rewards", hotspot_index, "total_rewards"],
                        "Total Rewards",
                        hotspot_token,
                        "mdi:hand-coin-outline",
                    )
                )

            for token in rewards["rewards_aggregated"]:
                sensors.append(
                    HotspotReward(
                        api_backend,
                        wallet,
                        wallet,
                        ["rewards_aggregated", token, "claimed_rewards"],
                        "Claimed Rewards",
                        token,
                        "mdi:hand-coin-outline",
                    )
                )
                sensors.append(
                    HotspotReward(
                        api_backend,
                        wallet,
                        wallet,
                        ["rewards_aggregated", token, "unclaimed_rewards"],
                        "Unclaimed Rewards",
                        token,
                        "mdi:hand-coin-outline",
                    )
                )
                sensors.append(
                    HotspotReward(
                        api_backend,
                        wallet,
                        wallet,
                        ["rewards_aggregated", token, "total_rewards"],
                        "Total Rewards",
                        token,
                        "mdi:hand-coin-outline",
                    )
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
