"""DenonAvr3805Entity class"""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .const import CONF_HOST
from .const import CONF_NAME
from .const import DOMAIN
from .const import MANUFACTURER
from .const import NAME
from .const import VERSION


class DenonAvr3805Entity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def device_info(self):
        """Return device information."""
        device_name = self.config_entry.data.get(CONF_NAME, "Denon")
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": device_name,
            "model": "AVR-3805",
            "manufacturer": MANUFACTURER,
            "configuration_url": f"http://{self.config_entry.data.get(CONF_HOST)}"
        }


