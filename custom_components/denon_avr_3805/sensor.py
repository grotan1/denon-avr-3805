"""Sensor platform for Denon AVR-3805."""
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import SENSOR
from .entity import DenonAvr3805Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([
        DenonAvr3805VolumeSensor(coordinator, entry),
        DenonAvr3805InputSensor(coordinator, entry),
    ])


class DenonAvr3805VolumeSensor(DenonAvr3805Entity):
    """Denon AVR-3805 volume sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_volume"

    @property
    def state(self):
        """Return the state of the sensor."""
        volume = self.coordinator.data.get("volume")
        if volume and volume.startswith("MV"):
            return int(volume[2:])  # Extract level from MV50
        return None

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
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_input"

    @property
    def state(self):
        """Return the state of the sensor."""
        input_val = self.coordinator.data.get("input")
        if input_val and input_val.startswith("SI"):
            return input_val[2:]  # Extract input from SIVCR
        return None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:audio-input-rca"
