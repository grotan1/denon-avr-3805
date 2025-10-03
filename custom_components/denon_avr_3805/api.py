"""API Client for Denon AVR-3805 via serial over TCP (ser2net)."""
from __future__ import annotations

import asyncio
import logging
import socket
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    from collections.abc import Coroutine

_LOGGER: logging.Logger = logging.getLogger(__package__)


@dataclass
class ConnectionStats:
    """Connection statistics tracking."""
    successful_connections: int = 0
    failed_connections: int = 0
    total_commands: int = 0
    failed_commands: int = 0
    consecutive_failures: int = 0
    last_successful_connection: float | None = None
    last_failed_connection: float | None = None

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


class DenonAvr3805ApiClient:
    def __init__(self, host: str, port: int, config: dict[str, Any] | None = None) -> None:
        """Initialize the API client for TCP connection to ser2net."""
        self._host: str = host
        self._port: int = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock: asyncio.Lock = asyncio.Lock()  # To serialize commands

        # Enhanced configuration with defaults
        self._config = {
            'connection_timeout': 8.0,      # Increased from 5s
            'read_timeout': 3.0,
            'command_timeout': 10.0,
            'max_retries': 3,
            'retry_delay': 1.0,
            'exponential_backoff': True,
            'max_backoff': 30.0,
            **(config or {})
        }

        # Connection statistics
        self._stats = ConnectionStats()

    @property
    def connection_stats(self) -> ConnectionStats:
        """Get connection statistics."""
        return self._stats

    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        return (self._writer is not None and
                not self._writer.is_closing())

    async def connect(self) -> None:
        """Establish connection to ser2net with retry logic."""
        success = await self.connect_with_retry()
        if not success:
            raise ConnectionError(f"Failed to connect to {self._host}:{self._port} after retries")

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
                _LOGGER.debug("Connection attempt %d/%d failed: %s",
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
        return False

    async def _connect_tcp(self) -> None:
        """Establish TCP connection."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._config['connection_timeout']
            )

            # Drain any initial data
            await self._drain_input()

        except asyncio.TimeoutError:
            raise ConnectionError(f"Timeout connecting to {self._host}:{self._port}")
        except socket.gaierror as e:
            raise ConnectionError(f"DNS resolution failed for {self._host}: {e}")
        except ConnectionRefusedError:
            raise ConnectionError(f"Connection refused by {self._host}:{self._port}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self._host}:{self._port}: {e}")

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
                _LOGGER.debug("Disconnected from Denon AVR")

    async def _send_command(self, command: str, expected_prefix: str = None) -> Optional[str]:
        """Enhanced command sending with better error handling."""
        if not self.is_connected:
            raise ConnectionError("Not connected to AVR")

        async with self._lock:
            try:
                self._stats.total_commands += 1

                # Send command with carriage return
                full_command = (command + "\r").encode()
                _LOGGER.debug("Sending command: %s", command)

                self._writer.write(full_command)
                await asyncio.wait_for(
                    self._writer.drain(),
                    timeout=self._config['command_timeout']
                )

                # If no response expected (control commands), just return None
                if expected_prefix is None:
                    _LOGGER.debug("Control command sent (no response expected)")
                    return None

                # For status queries, read expected response with timeout
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

                # Check if this is the expected response
                if decoded.startswith(expected_prefix):
                    _LOGGER.debug("Found expected response: %s", decoded)
                    return decoded

                # Skip command echoes and confirmations
                if self._should_skip_response(decoded):
                    _LOGGER.debug("Skipping response: %s", decoded)
                    continue

                # Skip other unexpected responses
                _LOGGER.debug("Skipping unexpected response: %s", decoded)

            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout waiting for response with prefix: %s", expected_prefix)
                break
            except Exception as e:
                _LOGGER.debug("Error reading response: %s", e)
                break

        _LOGGER.debug("Failed to find expected response with prefix: %s", expected_prefix)
        return None

    def _should_skip_response(self, response: str) -> bool:
        """Determine if response should be skipped."""
        skip_patterns = [
            "PW?", "MV?", "MU?", "SI?", "SI ?", "CV?", "ZM?",
            "PWON", "PWSTANDBY", "MUON", "MUOFF"  # Command confirmations
        ]
        return response in skip_patterns

    async def async_power_on(self) -> None:
        """Turn the AVR on."""
        await self._send_command("PWON")

    async def async_power_off(self) -> None:
        """Turn the AVR to standby."""
        await self._send_command("PWSTANDBY")

    async def async_get_power_status(self) -> Optional[str]:
        """Get power status (PWON or PWSTANDBY)."""
        return await self._send_command("PW?", "PW")

    async def async_mute_on(self) -> None:
        """Mute the AVR."""
        await self._send_command("MUON")

    async def async_mute_off(self) -> None:
        """Unmute the AVR."""
        await self._send_command("MUOFF")

    async def async_get_mute_status(self) -> Optional[str]:
        """Get mute status (MUON or MUOFF)."""
        return await self._send_command("MU?", "MU")

    async def async_volume_up(self) -> None:
        """Increase volume."""
        await self._send_command("MVUP")

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        await self._send_command("MVDOWN")

    async def async_set_volume(self, level: int) -> None:
        """Set volume level (0-98)."""
        if not 0 <= level <= 98:
            raise ValueError("Volume level must be between 0 and 98")
        await self._send_command(f"MV{level:02d}")

    async def async_get_volume(self) -> Optional[str]:
        """Get current volume level."""
        return await self._send_command("MV?", "MV")

    async def async_select_input(self, input_code: str) -> None:
        """Select input (e.g., 'VCR', 'TV', 'DVD')."""
        await self._send_command(f"SI{input_code}")

    async def async_get_input(self) -> Optional[str]:
        """Get current input."""
        return await self._send_command("SI?", "SI")

    async def _drain_input(self) -> None:
        """Drain any pending input from the connection."""
        if not self._reader:
            return
        try:
            # Try to read any pending data with a very short timeout
            # Use read(1) instead of readuntil to avoid conflicts
            while True:
                data = await asyncio.wait_for(
                    self._reader.read(1), timeout=0.01
                )
                if not data:
                    break  # No more data
                # Continue reading until no more data
        except asyncio.TimeoutError:
            # No more data to drain
            pass
        except Exception as e:
            _LOGGER.debug("Error draining input: %s", e)
        """Get all status information at once (for debugging)."""
        status = {}
        queries = [
            ("power", "PW?"),
            ("volume", "MV?"),
            ("mute", "MU?"),
            ("input", "SI?"),
        ]

        for name, command in queries:
            try:
                response = await self._send_command(command)
                status[name] = response
                _LOGGER.debug("Query %s (%s) returned: %s", name, command, response)
            except Exception as e:
                _LOGGER.debug("Query %s (%s) failed: %s", name, command, e)
                status[name] = None

        return status

    async def async_get_volume_alt(self) -> Optional[str]:
        """Try alternative volume query methods."""
        # Try MV? again as fallback (CV? was returning power status)
        return await self._send_command("MV?", "MV")

    async def async_get_power_alt(self) -> Optional[str]:
        """Try alternative power query methods."""
        # Try PW? first
        response = await self._send_command("PW?", "PW")
        if response:
            return response
        # Some AVRs use ZM? for main zone power
        return await self._send_command("ZM?", "ZM")

    def get_diagnostics(self) -> dict[str, Any]:
        """Get diagnostic information for troubleshooting."""
        return {
            "connection": {
                "host": self._host,
                "port": self._port,
                "is_connected": self.is_connected,
            },
            "config": self._config,
            "stats": {
                "successful_connections": self._stats.successful_connections,
                "failed_connections": self._stats.failed_connections,
                "total_commands": self._stats.total_commands,
                "failed_commands": self._stats.failed_commands,
                "consecutive_failures": self._stats.consecutive_failures,
                "success_rate": self._stats.success_rate,
                "is_healthy": self._stats.is_healthy,
                "last_successful_connection": self._stats.last_successful_connection,
                "last_failed_connection": self._stats.last_failed_connection,
            }
        }

    # Add more methods as needed for other AVR functions
