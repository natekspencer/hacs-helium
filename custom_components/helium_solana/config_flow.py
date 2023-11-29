"""Config flow for Helium Solana integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import (
    CONF_INTEGRATION,
    CONF_INTEGRATION_OPTIONS,
    CONF_VERSION,
    CONF_WALLET,
    DOMAIN,
    INTEGRATION_WALLET,
)

USER_SCHEMA = vol.Schema(
    {vol.Required(CONF_INTEGRATION): vol.In(CONF_INTEGRATION_OPTIONS)}
)
WALLET_SCHEMA = vol.Schema({vol.Required(CONF_WALLET): str})


class HeliumSolanaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 2

    data: dict[str, int | str] | None = None
    title: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        if user_input is not None:
            selected_integration = user_input[CONF_INTEGRATION]

            if selected_integration != INTEGRATION_WALLET:
                self._async_abort_entries_match(user_input)

            self.data = {}
            self.data[CONF_VERSION] = self.VERSION
            self.data[CONF_INTEGRATION] = selected_integration
            self.title = CONF_INTEGRATION_OPTIONS[selected_integration]

            if selected_integration == INTEGRATION_WALLET:
                return self.async_show_form(step_id="wallet", data_schema=WALLET_SCHEMA)

            return self.async_create_entry(title=self.title, data=self.data)

        return self.async_show_form(step_id="user", data_schema=USER_SCHEMA)

    async def async_step_wallet(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the wallet flow."""
        self.data[CONF_WALLET] = user_input[CONF_WALLET]
        self._async_abort_entries_match(self.data)
        self.title = f"{self.title} {self.data[CONF_WALLET][0:4]}"
        return self.async_create_entry(title=self.title, data=self.data)
