"""Enhanced API Client for Denon AVR-3805 via serial over TCP (ser2net)."""
import asyncio
import logging
import socket
import time
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ConnectionState(Enum):
    """Connection state enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ConnectionStats:
    """Connection statistics tracking."""
    successful_connections: int = 0
    failed_connections: int = 0
    total_commands: int = 0
    failed_commands: int = 0
    last_successful_connection: Optional[float] = None
    last_failed_connection: Optional[float] = None
    consecutive_failures: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate connection success rate."""
        total = self.successful_connections + self.failed_connections
        if total == 0:
            return 1.0
        return self.successful_connections / total

    @property
    def is_healthy(self) -> bool:
        """Determine if connection is healthy."""
        return self.consecutive_failures < 3 and self.success_rate > 0.7


class EnhancedDenonAvr3805ApiClient:
    """Enhanced API client with robust connection handling."""

    def __init__(self, host: str, port: int, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the enhanced API client."""
        self._host = host
        self._port = port

        # Configuration with defaults
        self._config = {
            'connection_timeout': 8.0,      # Increased from 5s
            'read_timeout': 3.0,
            'command_timeout': 10.0,
            'max_retries': 3,
            'retry_delay': 1.0,
            'exponential_backoff': True,
            'max_backoff': 30.0,
            'health_check_interval': 300.0,  # 5 minutes
            'persistent_connection': False,   # Option for future enhancement
            **(config or {})
        }

        # Connection state
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._state = ConnectionState.DISCONNECTED
        self._stats = ConnectionStats()
        self._last_health_check = 0.0

    @property
    def connection_stats(self) -> ConnectionStats:
        """Get connection statistics."""
        return self._stats

    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        return (self._state == ConnectionState.CONNECTED and
                self._writer is not None and
                not self._writer.is_closing())

    async def connect_with_retry(self) -> bool:
        """Connect with retry logic and exponential backoff."""
        if self.is_connected:
            return True

        max_retries = self._config['max_retries']
        base_delay = self._config['retry_delay']

        for attempt in range(max_retries):
            try:
                success = await self._attempt_connection()
                if success:
                    self._stats.successful_connections += 1
                    self._stats.consecutive_failures = 0
                    self._stats.last_successful_connection = time.time()
                    return True

            except Exception as e:
                _LOGGER.warning("Connection attempt %d/%d failed: %s",
                              attempt + 1, max_retries, e)

            # Calculate backoff delay
            if attempt < max_retries - 1:  # Don't delay after last attempt
                if self._config['exponential_backoff']:
                    delay = min(base_delay * (2 ** attempt), self._config['max_backoff'])
                else:
                    delay = base_delay

                _LOGGER.debug("Waiting %.1fs before retry %d/%d",
                            delay, attempt + 2, max_retries)
                await asyncio.sleep(delay)

        # All attempts failed
        self._stats.failed_connections += 1
        self._stats.consecutive_failures += 1
        self._stats.last_failed_connection = time.time()
        self._state = ConnectionState.ERROR
        return False

    async def _attempt_connection(self) -> bool:
        """Single connection attempt."""
        self._state = ConnectionState.CONNECTING

        try:
            # Close any existing connection
            await self.disconnect()

            # Establish new connection
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._config['connection_timeout']
            )

            # Verify connection health
            if await self._verify_connection():
                self._state = ConnectionState.CONNECTED
                _LOGGER.info("Successfully connected to Denon AVR at %s:%s",
                           self._host, self._port)
                return True
            else:
                await self.disconnect()
                return False

        except (asyncio.TimeoutError, OSError, ConnectionError) as e:
            await self.disconnect()
            _LOGGER.debug("Connection attempt failed: %s", e)
            return False

    async def _verify_connection(self) -> bool:
        """Verify connection is working by sending a simple command."""
        try:
            # Send a simple query to verify connection
            response = await self._send_command_internal("PW?", "PW", verify=False)
            return response is not None
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Enhanced disconnect with proper cleanup."""
        if self._writer:
            try:
                if not self._writer.is_closing():
                    self._writer.close()
                    await asyncio.wait_for(
                        self._writer.wait_closed(),
                        timeout=2.0
                    )
            except Exception as e:
                _LOGGER.debug("Error during disconnect: %s", e)
            finally:
                self._reader = None
                self._writer = None
                self._state = ConnectionState.DISCONNECTED
                _LOGGER.debug("Disconnected from Denon AVR")

    async def send_command(self, command: str, expected_prefix: str = None) -> Optional[str]:
        """Enhanced command sending with automatic reconnection."""
        if not await self._ensure_connected():
            return None

        try:
            return await self._send_command_internal(command, expected_prefix)
        except (ConnectionError, OSError) as e:
            _LOGGER.warning("Command failed due to connection issue: %s", e)
            self._state = ConnectionState.ERROR

            # Try to reconnect and retry once
            if await self.connect_with_retry():
                try:
                    return await self._send_command_internal(command, expected_prefix)
                except Exception as retry_e:
                    _LOGGER.error("Retry after reconnection failed: %s", retry_e)

            return None

    async def _ensure_connected(self) -> bool:
        """Ensure we have a healthy connection."""
        current_time = time.time()

        # Periodic health check
        if (current_time - self._last_health_check >
            self._config['health_check_interval']):
            await self._perform_health_check()
            self._last_health_check = current_time

        if not self.is_connected:
            return await self.connect_with_retry()

        return True

    async def _perform_health_check(self) -> None:
        """Perform periodic connection health check."""
        if not self.is_connected:
            return

        try:
            # Send a simple ping command
            response = await asyncio.wait_for(
                self._send_command_internal("PW?", "PW", verify=False),
                timeout=self._config['read_timeout']
            )

            if response is None:
                _LOGGER.warning("Health check failed - no response")
                self._state = ConnectionState.ERROR
                await self.disconnect()
            else:
                _LOGGER.debug("Health check passed")

        except Exception as e:
            _LOGGER.warning("Health check failed: %s", e)
            self._state = ConnectionState.ERROR
            await self.disconnect()

    async def _send_command_internal(self, command: str, expected_prefix: str = None,
                                   verify: bool = True) -> Optional[str]:
        """Internal command sending implementation."""
        if verify and not self.is_connected:
            raise ConnectionError("Not connected to AVR")

        async with self._lock:
            try:
                self._stats.total_commands += 1

                # Send command
                full_command = (command + "\r").encode()
                _LOGGER.debug("Sending command: %s", command)

                self._writer.write(full_command)
                await asyncio.wait_for(
                    self._writer.drain(),
                    timeout=self._config['command_timeout']
                )

                # Handle response
                if expected_prefix is None:
                    _LOGGER.debug("Control command sent (no response expected)")
                    return None

                response = await asyncio.wait_for(
                    self._read_expected_response(expected_prefix),
                    timeout=self._config['command_timeout']
                )

                return response

            except asyncio.TimeoutError:
                self._stats.failed_commands += 1
                _LOGGER.warning("Command timeout: %s", command)
                return None
            except Exception as e:
                self._stats.failed_commands += 1
                _LOGGER.error("Command failed %s: %s", command, e)
                raise

    async def _read_expected_response(self, expected_prefix: str) -> Optional[str]:
        """Enhanced response reading with better timeout handling."""
        start_time = time.time()
        timeout = self._config['read_timeout']

        while time.time() - start_time < timeout:
            try:
                response = await asyncio.wait_for(
                    self._reader.readuntil(b"\r"),
                    timeout=min(1.0, timeout - (time.time() - start_time))
                )

                decoded = response.decode().strip()
                _LOGGER.debug("Received response: %s", decoded)

                if decoded.startswith(expected_prefix):
                    return decoded

                # Skip command echoes and invalid responses
                if self._should_skip_response(decoded):
                    continue

            except asyncio.TimeoutError:
                break
            except Exception as e:
                _LOGGER.debug("Error reading response: %s", e)
                break

        return None

    def _should_skip_response(self, response: str) -> bool:
        """Determine if response should be skipped."""
        skip_patterns = [
            "PW?", "MV?", "MU?", "SI?", "SI ?", "CV?", "ZM?",
            "PWON", "PWSTANDBY", "MUON", "MUOFF"  # Command confirmations
        ]
        return response in skip_patterns

    # Keep all existing command methods but use enhanced send_command
    async def async_power_on(self) -> None:
        """Turn the AVR on."""
        await self.send_command("PWON")

    async def async_power_off(self) -> None:
        """Turn the AVR to standby."""
        await self.send_command("PWSTANDBY")

    async def async_get_power_status(self) -> Optional[str]:
        """Get power status (PWON or PWSTANDBY)."""
        return await self.send_command("PW?", "PW")

    # ... (include all other existing methods)

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information."""
        return {
            "connection_state": self._state.value,
            "is_connected": self.is_connected,
            "stats": {
                "successful_connections": self._stats.successful_connections,
                "failed_connections": self._stats.failed_connections,
                "total_commands": self._stats.total_commands,
                "failed_commands": self._stats.failed_commands,
                "success_rate": self._stats.success_rate,
                "consecutive_failures": self._stats.consecutive_failures,
                "is_healthy": self._stats.is_healthy,
            },
            "config": self._config,
            "host": self._host,
            "port": self._port,
        }