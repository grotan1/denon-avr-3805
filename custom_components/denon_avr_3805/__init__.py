"""
Custom integration to integrate Denon AVR-3805 with Home Assistant.

For more details about this integration, please refer to
https://github.com/grotan1/denon-avr-3805
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import DenonAvr3805ApiClient
from .const import CONF_HOST
from .const import CONF_PORT
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT)

    client = DenonAvr3805ApiClient(host, port)

    coordinator = DenonAvr3805DataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    platforms_to_setup = []
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            platforms_to_setup.append(platform)

    if platforms_to_setup:
        await hass.config_entries.async_forward_entry_setups(entry, platforms_to_setup)

    entry.add_update_listener(async_update_entry)
    return True


class DenonAvr3805DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DenonAvr3805ApiClient,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Enhanced update with better error handling and retry logic."""
        try:
            # Use enhanced connection with retry logic
            if not await self.api.connect_with_retry():
                raise UpdateFailed("Failed to connect to AVR after retries")

            # Give AVR time to be ready after connection
            await asyncio.sleep(0.3)  # Reduced from 0.5s for efficiency

            data = {}

            # Query power status with fallback
            try:
                power_status = await self.api.async_get_power_status()
                if not power_status:
                    # Try alternative power query
                    power_status = await self.api.async_get_power_alt()
                data["power"] = power_status
                _LOGGER.debug("Power status query returned: %s", power_status)
            except Exception as e:
                _LOGGER.debug("Power status query failed: %s", e)
                data["power"] = None

            # Small delay between queries to avoid overwhelming the AVR
            await asyncio.sleep(0.1)  # Reduced from 0.2s

            try:
                volume_status = await self.api.async_get_volume()
                if not volume_status:
                    # Try alternative volume query
                    volume_status = await self.api.async_get_volume_alt()
                data["volume"] = volume_status
                _LOGGER.debug("Volume status query returned: %s", volume_status)
            except Exception as e:
                _LOGGER.debug("Volume status query failed: %s", e)
                data["volume"] = None

            # Small delay between queries to avoid overwhelming the AVR
            await asyncio.sleep(0.1)

            try:
                mute_status = await self.api.async_get_mute_status()
                data["mute"] = mute_status
                _LOGGER.debug("Mute status query returned: %s", mute_status)
            except Exception as e:
                _LOGGER.debug("Mute status query failed: %s", e)
                data["mute"] = None

            await asyncio.sleep(0.1)

            try:
                input_status = await self.api.async_get_input()
                data["input"] = input_status
                _LOGGER.debug("Input status query returned: %s", input_status)
            except Exception as e:
                _LOGGER.debug("Input status query failed: %s", e)
                data["input"] = None

            await asyncio.sleep(0.1)

            # Try additional queries that might work better with this AVR
            try:
                # Some AVRs respond better to different query formats
                alt_input = await self.api._send_command("SI ?")
                if alt_input and alt_input != input_status:
                    _LOGGER.debug("Alternative input query returned: %s", alt_input)
                    if input_status is None and alt_input:
                        data["input"] = alt_input
            except Exception as e:
                _LOGGER.debug("Alternative input query failed: %s", e)

            await self.api.disconnect()

            # Log diagnostics periodically for troubleshooting
            if self.api.connection_stats.total_commands % 50 == 0:
                stats = self.api.connection_stats
                _LOGGER.info("Connection stats - Success rate: %.1f%%, Commands: %d, Failures: %d",
                           stats.success_rate * 100, stats.total_commands, stats.failed_commands)

            _LOGGER.debug("Coordinator update completed - Power: %s, Volume: %s, Mute: %s, Input: %s",
                         data.get("power"), data.get("volume"), data.get("mute"), data.get("input"))
            return data

        except UpdateFailed:
            # Re-raise UpdateFailed exceptions
            raise
        except Exception as exception:
            _LOGGER.error("Unexpected error during update: %s", exception)
            raise UpdateFailed(f"Unexpected error: {exception}") from exception

    def get_diagnostics(self):
        """Get diagnostic information."""
        return {
            "coordinator": {
                "last_update_success": self.last_update_success,
                "last_exception": str(self.last_exception) if self.last_exception else None,
                "update_interval": str(self.update_interval),
                "data": self.data if self.data else {},
            },
            "api": self.api.get_diagnostics(),
        }


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Only unload platforms that were actually set up
    platforms_to_unload = coordinator.platforms if hasattr(coordinator, 'platforms') else PLATFORMS
    
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in platforms_to_unload
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update config entry."""
    # Only reload if platform options changed, not if just connection data changed
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Check if platform configuration changed
    current_platforms = set(coordinator.platforms)
    new_platforms = {platform for platform in PLATFORMS if entry.options.get(platform, True)}
    
    if current_platforms != new_platforms:
        # Platform configuration changed, need to reload
        await async_reload_entry(hass, entry)
    else:
        # Only connection data changed, just update coordinator
        coordinator.api.host = entry.data.get(CONF_HOST)
        coordinator.api.port = entry.data.get(CONF_PORT)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
