"""Data coordinator for Span MAIN 40 integration."""
from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DEFAULT_PORT
from .span_client import SpanPanelClient

_LOGGER = logging.getLogger(__name__)


class SpanPanelCoordinator:
    """Manage the gRPC connection and data for a Span panel."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self._client = SpanPanelClient(
            host=entry.data["host"],
            port=entry.data.get("port", DEFAULT_PORT),
        )
        self._listeners: list[callback] = []

    @property
    def client(self) -> SpanPanelClient:
        """Return the client."""
        return self._client

    @property
    def data(self):
        """Return current panel data."""
        return self._client.data

    async def async_setup(self) -> bool:
        """Connect to the panel and start streaming."""
        if not await self._client.connect():
            return False

        # Register for updates from the client
        self._client.register_callback(self._on_data_update)

        # Start the metric stream
        await self._client.start_streaming()
        return True

    async def async_shutdown(self) -> None:
        """Disconnect from the panel."""
        await self._client.disconnect()

    @callback
    def _on_data_update(self) -> None:
        """Handle data update from gRPC stream."""
        for listener in self._listeners:
            try:
                listener()
            except Exception:
                _LOGGER.exception("Error calling listener")

    def async_add_listener(self, update_callback: callback) -> callback:
        """Add a listener for data updates. Returns unregister function."""
        self._listeners.append(update_callback)

        def remove():
            if update_callback in self._listeners:
                self._listeners.remove(update_callback)

        return remove
