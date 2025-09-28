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
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_volume"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_volume"

    @property
    def state(self):
        """Return the state of the sensor."""
        volume_response = self.coordinator.data.get("volume")
        if volume_response and isinstance(volume_response, str):
            # Handle different volume response formats
            if volume_response.startswith("MV"):
                try:
                    # MVxx format (xx is volume level)
                    vol_str = volume_response[2:]
                    if vol_str.isdigit():
                        return int(vol_str)
                except (ValueError, IndexError):
                    pass
            elif volume_response.isdigit():
                # Just digits (raw volume level)
                try:
                    return int(volume_response)
                except ValueError:
                    pass
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
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_input"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_input"

    @property
    def state(self):
        """Return the state of the sensor."""
        input_response = self.coordinator.data.get("input")
        if input_response and isinstance(input_response, str):
            # Handle different input response formats
            if input_response.startswith("SI"):
                # SI<source> format - extract source after SI
                source = input_response[2:]
                # Only return if we have a non-empty source
                return source if source else None
            elif len(input_response) > 0:
                # Raw input name - but filter out obviously invalid responses
                # Some AVRs might return status messages instead of input names
                if input_response in ["ON", "OFF", "STANDBY", "PWON", "PWSTANDBY"]:
                    return None
                return input_response
        return None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:audio-input-rca"
