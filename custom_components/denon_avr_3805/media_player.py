"""Media player platform for Denon AVR-3805."""
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.const import STATE_OFF, STATE_ON

from .const import CONF_NAME
from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import MEDIA_PLAYER
from .const import NAME
from .entity import DenonAvr3805Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup media_player platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([DenonAvr3805MediaPlayer(coordinator, entry)])


class DenonAvr3805MediaPlayer(DenonAvr3805Entity, MediaPlayerEntity):
    """Denon AVR-3805 media player class."""

    @property
    def unique_id(self):
        """Return a unique ID for this entity."""
        return f"{self.config_entry.entry_id}_media_player"

    @property
    def name(self):
        """Return the name of the media player (empty for device name only)."""
        return ""

    @property
    def translation_key(self):
        """Return the translation key for this entity."""
        return "media_player"

    @property
    def icon(self):
        """Return the icon of the media player."""
        return "mdi:amplifier"

    @property
    def state(self):
        """Return the state of the media player."""
        power_status = self.coordinator.data.get("power")
        if power_status and isinstance(power_status, str):
            if power_status in ["PWON", "ON", "ZM ON"]:
                return STATE_ON
        return STATE_OFF

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        volume_response = self.coordinator.data.get("volume")
        if volume_response and isinstance(volume_response, str):
            # Handle different volume response formats
            if volume_response.startswith("MV"):
                try:
                    vol_str = volume_response[2:]
                    if vol_str.isdigit():
                        level = int(vol_str)
                        return level / 98.0  # Denon uses 0-98 scale
                except (ValueError, IndexError):
                    pass
            elif volume_response.isdigit():
                try:
                    level = int(volume_response)
                    return level / 98.0
                except ValueError:
                    pass
        return None

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        mute_status = self.coordinator.data.get("mute")
        if mute_status and isinstance(mute_status, str):
            return mute_status in ["MUON", "ON"]
        return False

    @property
    def source(self):
        """Return the current input source."""
        input_response = self.coordinator.data.get("input")
        if input_response and isinstance(input_response, str):
            if input_response.startswith("SI"):
                source = input_response[2:]
                return source if source else None
            elif len(input_response) > 0:
                if input_response in ["ON", "OFF", "STANDBY", "PWON", "PWSTANDBY"]:
                    return None
                return input_response
        return None

    @property
    def source_list(self):
        """List of available input sources."""
        return [
            "VCR", "DVD", "TV", "CD", "TUNER", "AUX", "NET", "USB",
            "PHONO", "DVR", "CBL/SAT", "V.AUX", "DOCK", "IPOD",
            "BD", "HDRADIO", "SIRIUS", "GAME", "GAME2", "VAUX",
            "DOCK", "IPD", "IRP", "FVP"
        ]

    async def async_turn_on(self):
        """Turn the media player on."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_power_on()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        """Turn the media player off."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_power_off()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        level = int(volume * 98)  # Convert to 0-98 scale
        await self.coordinator.api.connect()
        await self.coordinator.api.async_set_volume(level)
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self):
        """Volume up the media player."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_volume_up()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_volume_down(self):
        """Volume down the media player."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_volume_down()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        await self.coordinator.api.connect()
        if mute:
            await self.coordinator.api.async_mute_on()
        else:
            await self.coordinator.api.async_mute_off()
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source):
        """Select input source."""
        await self.coordinator.api.connect()
        await self.coordinator.api.async_select_input(source)
        await self.coordinator.api.disconnect()
        await self.coordinator.async_request_refresh()