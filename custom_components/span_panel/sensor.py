"""Sensor platform for Span MAIN 40 integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
)
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
    """Set up Span Panel sensors from a config entry."""
    coordinator: SpanPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    # Main feed sensors
    entities.extend([
        SpanMainPowerSensor(coordinator, entry),
        SpanMainVoltageSensor(coordinator, entry),
        SpanMainCurrentSensor(coordinator, entry),
        SpanMainFrequencySensor(coordinator, entry),
    ])

    # Per-circuit sensors
    for circuit_id, circuit_info in coordinator.data.circuits.items():
        entities.extend([
            SpanCircuitPowerSensor(coordinator, entry, circuit_id),
            SpanCircuitVoltageSensor(coordinator, entry, circuit_id),
            SpanCircuitCurrentSensor(coordinator, entry, circuit_id),
        ])

    async_add_entities(entities)


class SpanBaseSensor(SensorEntity):
    """Base class for Span sensors."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: SpanPanelCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._entry = entry
        self._remove_listener = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.data["host"])},
            name="Span MAIN 40",
            manufacturer="Span",
            model="MAIN 40 (Gen3)",
            sw_version=self._coordinator.data.firmware or None,
        )

    async def async_added_to_hass(self) -> None:
        """Register for updates when added to HA."""
        self._remove_listener = self._coordinator.async_add_listener(
            self._handle_update
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister when removed from HA."""
        if self._remove_listener:
            self._remove_listener()

    @callback
    def _handle_update(self) -> None:
        """Handle coordinator data update."""
        self.async_write_ha_state()


class SpanMainPowerSensor(SpanBaseSensor):
    """Main feed power sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data['host']}_main_power"
        self._attr_name = "Main Feed Power"

    @property
    def native_value(self) -> float | None:
        m = self._coordinator.data.main_feed
        return round(m.power_w, 1) if m else None


class SpanMainVoltageSensor(SpanBaseSensor):
    """Main feed voltage sensor."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data['host']}_main_voltage"
        self._attr_name = "Main Feed Voltage"

    @property
    def native_value(self) -> float | None:
        m = self._coordinator.data.main_feed
        return round(m.voltage_v, 1) if m else None


class SpanMainCurrentSensor(SpanBaseSensor):
    """Main feed current sensor."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data['host']}_main_current"
        self._attr_name = "Main Feed Current"

    @property
    def native_value(self) -> float | None:
        m = self._coordinator.data.main_feed
        return round(m.current_a, 1) if m else None


class SpanMainFrequencySensor(SpanBaseSensor):
    """Main feed frequency sensor."""

    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data['host']}_main_frequency"
        self._attr_name = "Main Feed Frequency"

    @property
    def native_value(self) -> float | None:
        m = self._coordinator.data.main_feed
        return round(m.frequency_hz, 2) if m and m.frequency_hz > 0 else None


class SpanCircuitSensor(SpanBaseSensor):
    """Base class for per-circuit sensors."""

    def __init__(
        self,
        coordinator: SpanPanelCoordinator,
        entry: ConfigEntry,
        circuit_id: int,
    ) -> None:
        super().__init__(coordinator, entry)
        self._circuit_id = circuit_id

    @property
    def _circuit_info(self):
        return self._coordinator.data.circuits.get(self._circuit_id)

    @property
    def _circuit_metrics(self):
        return self._coordinator.data.metrics.get(self._circuit_id)

    @property
    def device_info(self) -> DeviceInfo:
        info = self._circuit_info
        name = info.name if info else f"Circuit {self._circuit_id}"
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.data['host']}_circuit_{self._circuit_id}")},
            name=name,
            manufacturer="Span",
            model="Circuit Breaker",
            via_device=(DOMAIN, self._entry.data["host"]),
        )


class SpanCircuitPowerSensor(SpanCircuitSensor):
    """Per-circuit power sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator, entry, circuit_id):
        super().__init__(coordinator, entry, circuit_id)
        self._attr_unique_id = f"{entry.data['host']}_circuit_{circuit_id}_power"
        self._attr_name = "Power"

    @property
    def native_value(self) -> float | None:
        m = self._circuit_metrics
        return round(m.power_w, 1) if m else None


class SpanCircuitVoltageSensor(SpanCircuitSensor):
    """Per-circuit voltage sensor."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry, circuit_id):
        super().__init__(coordinator, entry, circuit_id)
        self._attr_unique_id = f"{entry.data['host']}_circuit_{circuit_id}_voltage"
        self._attr_name = "Voltage"

    @property
    def native_value(self) -> float | None:
        m = self._circuit_metrics
        return round(m.voltage_v, 1) if m else None


class SpanCircuitCurrentSensor(SpanCircuitSensor):
    """Per-circuit current sensor."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, entry, circuit_id):
        super().__init__(coordinator, entry, circuit_id)
        self._attr_unique_id = f"{entry.data['host']}_circuit_{circuit_id}_current"
        self._attr_name = "Current"

    @property
    def native_value(self) -> float | None:
        m = self._circuit_metrics
        return round(m.current_a, 3) if m else None
