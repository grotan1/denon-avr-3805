"""Support for Denon AVR-3805 sensors."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import DenonAvr3805Entity

if TYPE_CHECKING:
    from . import DenonAvr3805DataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""
    coordinator: DenonAvr3805DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DenonAvr3805VolumeSensor(coordinator, entry),
        DenonAvr3805InputSensor(coordinator, entry),
    ]

    async_add_devices(entities)


class DenonAvr3805VolumeSensor(DenonAvr3805Entity):
    """Denon AVR-3805 volume sensor class."""

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_volume"

    @property
    def translation_key(self) -> str:
        """Return the translation key for this entity."""
        return "volume"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("volume")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:volume-high"


class DenonAvr3805InputSensor(DenonAvr3805Entity):
    """Denon AVR-3805 input sensor class."""

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_input"

    @property
    def translation_key(self):
        """Return the translation key for this entity."""
        return "input"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("input")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:audio-input-rca"
