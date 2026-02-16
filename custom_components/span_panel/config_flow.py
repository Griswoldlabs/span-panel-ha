"""Config flow for Span MAIN 40 integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_PORT
from .span_client import SpanPanelClient

_LOGGER = logging.getLogger(__name__)


class SpanPanelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Span MAIN 40."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input["host"]
            port = user_input.get("port", DEFAULT_PORT)

            # Check if already configured
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Test connection
            client = SpanPanelClient(host, port)
            if await client.test_connection():
                return self.async_create_entry(
                    title=f"Span Panel ({host})",
                    data={"host": host, "port": port},
                )
            errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Optional("port", default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
