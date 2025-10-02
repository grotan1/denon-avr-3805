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
    def name(self):
        """Return the name of the binary_sensor."""
        device_name = self.config_entry.data.get(CONF_NAME, NAME)
        return f"{device_name} Connectivity"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return "connectivity"

    @property
    def is_on(self):
        """Return true if the AVR is connected."""
        return self.coordinator.last_update_success
