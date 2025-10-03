"""Enhanced coordinator with adaptive update intervals and better error handling."""

import asyncio
import logging
from datetime import timedelta
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_interval

from .enhanced_api import EnhancedDenonAvr3805ApiClient, ConnectionState

_LOGGER = logging.getLogger(__name__)


class EnhancedDenonAvr3805DataUpdateCoordinator(DataUpdateCoordinator):
    """Enhanced coordinator with adaptive behavior and robust error handling."""

    def __init__(self, hass: HomeAssistant, client: EnhancedDenonAvr3805ApiClient) -> None:
        """Initialize enhanced coordinator."""
        self.api = client
        self.platforms = []
        
        # Adaptive update intervals
        self._base_interval = timedelta(seconds=30)
        self._fast_interval = timedelta(seconds=15)
        self._slow_interval = timedelta(seconds=60)
        self._error_interval = timedelta(seconds=120)
        
        # State tracking
        self._consecutive_failures = 0
        self._last_successful_update = None
        self._update_mode = "normal"  # normal, fast, slow, error
        
        super().__init__(
            hass,
            _LOGGER,
            name="denon_avr_3805",
            update_interval=self._base_interval,
        )
        
        # Set up adaptive interval tracking
        self._setup_adaptive_intervals()
    
    def _setup_adaptive_intervals(self) -> None:
        """Set up adaptive update interval logic."""
        
        async def _adaptive_update_check(now):
            """Check if we should adjust update interval."""
            stats = self.api.connection_stats
            
            # Determine appropriate update mode
            new_mode = self._calculate_update_mode(stats)
            
            if new_mode != self._update_mode:
                _LOGGER.info("Changing update mode from %s to %s", 
                           self._update_mode, new_mode)
                self._update_mode = new_mode
                self._apply_update_mode()
        
        # Check every 2 minutes for interval adjustments
        async_track_time_interval(
            self.hass, _adaptive_update_check, timedelta(minutes=2)
        )
    
    def _calculate_update_mode(self, stats) -> str:
        """Calculate appropriate update mode based on connection statistics."""
        if not stats.is_healthy or stats.consecutive_failures >= 5:
            return "error"
        elif stats.consecutive_failures >= 2:
            return "slow"
        elif stats.success_rate < 0.8:
            return "slow"
        elif self._consecutive_failures == 0 and stats.success_rate > 0.95:
            # Only use fast mode if we're performing very well
            return "fast"
        else:
            return "normal"
    
    def _apply_update_mode(self) -> None:
        """Apply the current update mode settings."""
        mode_intervals = {
            "fast": self._fast_interval,
            "normal": self._base_interval,
            "slow": self._slow_interval,
            "error": self._error_interval,
        }
        
        new_interval = mode_intervals.get(self._update_mode, self._base_interval)
        
        if new_interval != self.update_interval:
            _LOGGER.info("Adjusting update interval to %s (mode: %s)", 
                        new_interval, self._update_mode)
            self.update_interval = new_interval
    
    async def _async_update_data(self) -> Dict[str, Any]:
        """Enhanced update with better error handling and recovery."""
        try:
            # Ensure connection before starting queries
            if not await self.api.connect_with_retry():
                self._consecutive_failures += 1
                raise UpdateFailed("Failed to connect to AVR after retries")
            
            # Perform queries with enhanced error handling
            data = await self._perform_queries()
            
            # Update success tracking
            self._consecutive_failures = 0
            self._last_successful_update = asyncio.get_event_loop().time()
            
            _LOGGER.debug("Update completed successfully: %s", data)
            return data
            
        except UpdateFailed:
            # Re-raise UpdateFailed exceptions
            self._consecutive_failures += 1
            raise
        except Exception as exception:
            self._consecutive_failures += 1
            _LOGGER.error("Unexpected error during update: %s", exception)
            raise UpdateFailed(f"Unexpected error: {exception}") from exception
        finally:
            # Always disconnect to free resources
            await self.api.disconnect()
    
    async def _perform_queries(self) -> Dict[str, Any]:
        """Perform all status queries with optimized error handling."""
        data = {}
        
        # Define queries with fallback options
        queries = [
            {
                'name': 'power',
                'primary': ('PW?', 'PW'),
                'fallback': ('ZM?', 'ZM'),
                'critical': True  # Power status is critical
            },
            {
                'name': 'volume',
                'primary': ('MV?', 'MV'),
                'fallback': None,
                'critical': False
            },
            {
                'name': 'mute',
                'primary': ('MU?', 'MU'),
                'fallback': None,
                'critical': False
            },
            {
                'name': 'input',
                'primary': ('SI?', 'SI'),
                'fallback': ('SI ?', 'SI'),
                'critical': False
            },
        ]
        
        critical_failures = 0
        
        for query_info in queries:
            name = query_info['name']
            
            try:
                # Try primary query
                result = await self._execute_query(query_info['primary'])
                
                # Try fallback if primary failed
                if result is None and query_info['fallback']:
                    _LOGGER.debug("Primary query failed for %s, trying fallback", name)
                    result = await self._execute_query(query_info['fallback'])
                
                data[name] = result
                
                if result is None and query_info['critical']:
                    critical_failures += 1
                    _LOGGER.warning("Critical query failed: %s", name)
                
                # Small delay between queries to avoid overwhelming AVR
                await asyncio.sleep(0.1)
                
            except Exception as e:
                _LOGGER.debug("Query %s failed: %s", name, e)
                data[name] = None
                
                if query_info['critical']:
                    critical_failures += 1
        
        # If too many critical queries failed, raise UpdateFailed
        if critical_failures > 0:
            _LOGGER.warning("Critical queries failed, marking update as failed")
            # Don't raise exception, but log the issue
            # This allows partial data updates
        
        return data
    
    async def _execute_query(self, query_params) -> Optional[str]:
        """Execute a single query with timeout."""
        command, expected_prefix = query_params
        
        try:
            return await asyncio.wait_for(
                self.api.send_command(command, expected_prefix),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            _LOGGER.debug("Query timeout: %s", command)
            return None
    
    async def async_refresh_forced(self) -> None:
        """Force immediate refresh regardless of interval."""
        _LOGGER.info("Forcing immediate refresh")
        await self.async_request_refresh()
    
    async def async_set_update_interval(self, interval_seconds: int) -> None:
        """Dynamically adjust update interval."""
        new_interval = timedelta(seconds=interval_seconds)
        _LOGGER.info("Manually setting update interval to %s", new_interval)
        self.update_interval = new_interval
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic information."""
        api_diagnostics = self.api.get_diagnostics()
        
        return {
            "coordinator": {
                "last_update_success": self.last_update_success,
                "last_exception": str(self.last_exception) if self.last_exception else None,
                "update_interval": str(self.update_interval),
                "update_mode": self._update_mode,
                "consecutive_failures": self._consecutive_failures,
                "last_successful_update": self._last_successful_update,
            },
            "api": api_diagnostics,
            "data": self.data if self.data else {},
        }
    
    @property
    def connection_healthy(self) -> bool:
        """Check if connection is considered healthy."""
        return (
            self.last_update_success and
            self._consecutive_failures < 3 and
            self.api.connection_stats.is_healthy
        )