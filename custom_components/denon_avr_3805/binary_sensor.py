"""Binary sensor platform for Denon AVR-3805."""
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import BINARY_SENSOR
from .const import BINARY_SENSOR_DEVICE_CLASS
from .const import CONF_NAME
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import NAME
from .entity import DenonAvr3805Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([DenonAvr3805BinarySensor(coordinator, entry)])


class DenonAvr3805BinarySensor(DenonAvr3805Entity, BinarySensorEntity):
    """denon_avr_3805 binary_sensor class."""

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_connectivity"

    @property
    def translation_key(self):
        """Return the translation key for this entity."""
        return "connectivity"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return "connectivity"

    @property
    def is_on(self):
        """Return true if the AVR is connected and responding."""
        # Check if coordinator has data and API connection is healthy
        if not self.coordinator.last_update_success:
            return False

        # Check if we have valid data indicating AVR is actually responding
        if self.coordinator.data:
            # At least one valid response indicates connection is working
            valid_responses = any(
                value is not None
                for key, value in self.coordinator.data.items()
                if key in ['power', 'volume', 'mute', 'input']
            )
            return valid_responses

        return False

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        if not self.coordinator.api:
            return {}

        stats = self.coordinator.api.connection_stats
        attributes = {
            "tcp_connected": self.coordinator.api.is_connected,
            "last_update_success": self.coordinator.last_update_success,
            "success_rate": round(stats.success_rate * 100, 1),
            "consecutive_failures": stats.consecutive_failures,
            "total_commands": stats.total_commands,
        }

        # Add data validity information
        if self.coordinator.data:
            attributes.update({
                "power_status": self.coordinator.data.get("power"),
                "volume_status": self.coordinator.data.get("volume"),
                "mute_status": self.coordinator.data.get("mute"),
                "input_status": self.coordinator.data.get("input"),
            })

        return attributes
