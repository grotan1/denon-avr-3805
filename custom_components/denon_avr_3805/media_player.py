"""Media player platform for Denon AVR-3805."""
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player import MediaPlayerEntityFeature
from homeassistant.const import STATE_OFF, STATE_ON

from .const import DEFAULT_NAME
from .const import DOMAIN
from .const import MEDIA_PLAYER
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
        """Return the name of the media player."""
        return f"{DEFAULT_NAME}_{MEDIA_PLAYER}"

    @property
    def state(self):
        """Return the state of the media player."""
        if self.coordinator.data.get("power") == "PWON":
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
        volume = self.coordinator.data.get("volume")
        if volume and volume.startswith("MV"):
            level = int(volume[2:])
            return level / 98.0  # Denon uses 0-98 scale
        return None

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self.coordinator.data.get("mute") == "MUON"

    @property
    def source(self):
        """Return the current input source."""
        input_val = self.coordinator.data.get("input")
        if input_val and input_val.startswith("SI"):
            return input_val[2:]
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