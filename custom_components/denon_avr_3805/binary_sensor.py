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
    def name(self):
        """Return the name of the binary_sensor."""
        device_name = self.config_entry.data.get(CONF_NAME, NAME)
        # Try to get translated "Connectivity" string
        try:
            connectivity_text = self.hass.helpers.translation.get_translated_string(
                ["component.denon_avr_3805.entity.binary_sensor.connectivity.name"],
                language=self.hass.config.language
            )
        except:
            connectivity_text = "Connectivity"
        return f"{device_name} {connectivity_text}"

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return "connectivity"

    @property
    def is_on(self):
        """Return true if the AVR is connected."""
        return self.coordinator.last_update_success
