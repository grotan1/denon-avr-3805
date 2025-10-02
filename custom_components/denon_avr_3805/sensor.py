"""Sensor platform for Denon AVR-3805."""
from .const import CONF_NAME
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import NAME
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
    def translation_key(self):
        """Return the translation key for this entity."""
        return "volume"

    @property
    def name(self):
        """Return the name of the sensor."""
        device_name = self.config_entry.data.get(CONF_NAME, NAME)
        return f"{device_name} Volume"

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
                        vol_int = int(vol_str)
                        # Validate volume range (0-98 for Denon)
                        if 0 <= vol_int <= 98:
                            return vol_int
                except (ValueError, IndexError):
                    pass
            elif volume_response.startswith("CV"):
                try:
                    # CVxx format (channel volume)
                    vol_str = volume_response[2:]
                    if vol_str.isdigit():
                        vol_int = int(vol_str)
                        if 0 <= vol_int <= 98:
                            return vol_int
                except (ValueError, IndexError):
                    pass
            elif volume_response.isdigit():
                # Just digits (raw volume level)
                try:
                    vol_int = int(volume_response)
                    if 0 <= vol_int <= 98:
                        return vol_int
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
    def translation_key(self):
        """Return the translation key for this entity."""
        return "input"

    @property
    def name(self):
        """Return the name of the sensor."""
        device_name = self.config_entry.data.get(CONF_NAME, NAME)
        return f"{device_name} Input"

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
                invalid_responses = [
                    "ON", "OFF", "STANDBY", "PWON", "PWSTANDBY",
                    "MUON", "MUOFF", "MV", "CV", "ZM", "ZMON", "ZMOFF"
                ]
                # Check if response starts with any invalid prefix
                if any(input_response.startswith(invalid) for invalid in invalid_responses):
                    return None
                # Check if response is exactly an invalid response
                if input_response in invalid_responses:
                    return None
                return input_response
        return None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:audio-input-rca"
