"""Switch platform for Denon AVR-3805."""
from homeassistant.components.switch import SwitchEntity

from .const import CONF_NAME
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import ICON
from .const import NAME
from .const import SWITCH
from .entity import DenonAvr3805Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([
        DenonAvr3805PowerSwitch(coordinator, entry),
        DenonAvr3805MuteSwitch(coordinator, entry),
    ])


class DenonAvr3805PowerSwitch(DenonAvr3805Entity, SwitchEntity):
    """Denon AVR-3805 power switch class."""

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_power"

    @property
    def translation_key(self):
        """Return the translation key for this entity."""
        return "power"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the AVR."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_power_on()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the AVR."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_power_off()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        device_name = self.config_entry.data.get(CONF_NAME, NAME)
        return f"{device_name} Power"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return "mdi:power"

    @property
    def is_on(self):
        """Return true if the AVR is on."""
        power_status = self.coordinator.data.get("power")
        if power_status and isinstance(power_status, str):
            # Handle different power response formats
            return power_status in ["PWON", "ON", "ZM ON"]
        return False


class DenonAvr3805MuteSwitch(DenonAvr3805Entity, SwitchEntity):
    """Denon AVR-3805 mute switch class."""

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_mute"

    @property
    def translation_key(self):
        """Return the translation key for this entity."""
        return "mute"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Mute the AVR."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_mute_on()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Unmute the AVR."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_mute_off()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    @property
    def name(self):
        """Return the name of the switch."""
        device_name = self.config_entry.data.get(CONF_NAME, NAME)
        return f"{device_name} Mute"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return "mdi:volume-off"

    @property
    def is_on(self):
        """Return true if the AVR is muted."""
        mute_status = self.coordinator.data.get("mute")
        if mute_status and isinstance(mute_status, str):
            # Handle different mute response formats
            return mute_status in ["MUON", "ON"]
        return False
