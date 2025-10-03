"""Diagnostics support for Denon AVR-3805."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

if TYPE_CHECKING:
    from . import DenonAvr3805DataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: DenonAvr3805DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    return coordinator.get_diagnostics()