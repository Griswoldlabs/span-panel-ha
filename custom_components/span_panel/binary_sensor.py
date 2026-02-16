"""Binary sensor platform for Span MAIN 40 integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SpanPanelCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Span Panel binary sensors from a config entry."""
    coordinator: SpanPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []

    for circuit_id in coordinator.data.circuits:
        entities.append(SpanBreakerStateSensor(coordinator, entry, circuit_id))

    async_add_entities(entities)


class SpanBreakerStateSensor(BinarySensorEntity):
    """Binary sensor for breaker state (ON/OFF based on voltage)."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(
        self,
        coordinator: SpanPanelCoordinator,
        entry: ConfigEntry,
        circuit_id: int,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._entry = entry
        self._circuit_id = circuit_id
        self._attr_unique_id = f"{entry.data['host']}_circuit_{circuit_id}_breaker"
        self._attr_name = "Breaker"
        self._remove_listener = None

    @property
    def device_info(self) -> DeviceInfo:
        info = self._coordinator.data.circuits.get(self._circuit_id)
        name = info.name if info else f"Circuit {self._circuit_id}"
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.data['host']}_circuit_{self._circuit_id}")},
            name=name,
            manufacturer="Span",
            model="Circuit Breaker",
            via_device=(DOMAIN, self._entry.data["host"]),
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if breaker is ON (voltage present)."""
        m = self._coordinator.data.metrics.get(self._circuit_id)
        if m is None:
            return None
        return m.is_on

    async def async_added_to_hass(self) -> None:
        self._remove_listener = self._coordinator.async_add_listener(
            self._handle_update
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_listener:
            self._remove_listener()

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
