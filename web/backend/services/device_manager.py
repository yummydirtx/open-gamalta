"""
Device Manager - Singleton for managing BLE connection lifecycle.

Wraps GamaltaClient and provides thread-safe access with state broadcasting.
"""

import asyncio
from collections.abc import Callable, Awaitable
from datetime import datetime

from gamalta import GamaltaClient
from gamalta.types import Mode, Color, LightningConfig
from gamalta.exceptions import GamaltaError, NotConnectedError, DeviceNotFoundError
from gamalta.transport.ble import BleTransport

from ..config import settings


StateCallback = Callable[[dict], Awaitable[None]]


class DeviceManager:
    """
    Singleton managing the BLE connection lifecycle.

    Key responsibilities:
    - Maintain single GamaltaClient instance
    - Handle connection/disconnection
    - Provide thread-safe access to client methods
    - Emit state changes via callbacks
    """

    def __init__(self):
        self._client: GamaltaClient | None = None
        self._lock = asyncio.Lock()
        self._state_callbacks: list[StateCallback] = []
        self._polling_task: asyncio.Task | None = None
        self._device_address: str | None = None
        self._device_name: str | None = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to a device."""
        return self._client is not None and self._client.is_connected

    @property
    def device_address(self) -> str | None:
        """Get the connected device's BLE address."""
        return self._device_address

    @property
    def device_name(self) -> str | None:
        """Get the connected device's name."""
        return self._device_name

    def add_state_callback(self, callback: StateCallback) -> None:
        """Register a callback to receive state updates."""
        if callback not in self._state_callbacks:
            self._state_callbacks.append(callback)

    def remove_state_callback(self, callback: StateCallback) -> None:
        """Unregister a state callback."""
        if callback in self._state_callbacks:
            self._state_callbacks.remove(callback)

    async def scan(self, timeout: float = 5.0) -> list[dict]:
        """
        Scan for Gamalta devices.

        Returns:
            List of dicts with 'address' and 'name' keys.
        """
        transport = BleTransport()
        devices = await transport.scan(timeout=timeout, name_filter="Gamalta")
        return [{"address": d.address, "name": d.name or "Unknown"} for d in devices]

    async def connect(self, address: str | None = None) -> str:
        """
        Connect to a Gamalta device.

        Args:
            address: Optional BLE address. If None, auto-discovers.

        Returns:
            Device name.

        Raises:
            DeviceNotFoundError: If no device found.
            ConnectionError: If connection fails.
        """
        async with self._lock:
            # Disconnect existing connection
            if self._client and self._client.is_connected:
                await self._client.disconnect()
                self._client = None

            self._client = GamaltaClient()
            await self._client.connect(address=address)

            # Store connection info
            self._device_address = address
            self._device_name = await self._client.query_name() or "Gamalta"

            # Start polling for state changes
            self._start_polling()

            # Broadcast connection state
            await self._broadcast_connection(True)

            return self._device_name

    async def disconnect(self) -> None:
        """Disconnect from the current device."""
        async with self._lock:
            self._stop_polling()
            if self._client:
                try:
                    await self._client.disconnect()
                except Exception:
                    pass
                self._client = None

            self._device_address = None
            self._device_name = None
            await self._broadcast_connection(False)

    async def get_state(self) -> dict:
        """
        Get current device state.

        Returns:
            Dict with power, mode, brightness, color.
        """
        if not self.is_connected:
            return {
                "connected": False,
                "power": False,
                "mode": 0,
                "mode_name": "MANUAL",
                "brightness": 0,
                "color": {"r": 0, "g": 0, "b": 0, "warm_white": 0, "cool_white": 0},
            }

        async with self._lock:
            try:
                state = await self._client.query_state()
                return self._format_state(state)
            except Exception:
                return {
                    "connected": True,
                    "power": False,
                    "mode": 0,
                    "mode_name": "MANUAL",
                    "brightness": 0,
                    "color": {"r": 0, "g": 0, "b": 0, "warm_white": 0, "cool_white": 0},
                }

    async def power_on(self) -> None:
        """Turn the light on."""
        await self._execute("power_on")

    async def power_off(self) -> None:
        """Turn the light off."""
        await self._execute("power_off")

    async def set_color(
        self, r: int, g: int, b: int, warm_white: int = 0, cool_white: int = 0
    ) -> None:
        """Set the light color (RGBWC)."""
        await self._execute("set_color", r, g, b, warm_white, cool_white)

    async def set_brightness(self, percent: int) -> None:
        """Set brightness (0-100)."""
        await self._execute("set_brightness", percent)

    async def set_mode(self, mode: Mode | int) -> None:
        """Set the operating mode."""
        if isinstance(mode, int):
            mode = Mode(mode)
        await self._execute("set_mode", mode)

    async def configure_lightning(self, config: LightningConfig) -> None:
        """Configure lightning effect schedule."""
        await self._execute("configure_lightning", config)

    async def preview_lightning(self) -> None:
        """Trigger a single lightning flash."""
        await self._execute("preview_lightning")

    async def set_name(self, name: str) -> None:
        """Set the device name."""
        await self._execute("set_name", name)
        self._device_name = name

    async def _execute(self, method: str, *args, **kwargs):
        """
        Execute a client method with proper locking.

        Args:
            method: Method name on GamaltaClient
            *args, **kwargs: Arguments to pass
        """
        if not self.is_connected:
            raise NotConnectedError("Not connected to device")

        async with self._lock:
            func = getattr(self._client, method)
            result = await func(*args, **kwargs)

            # Small delay for device to process, then broadcast state
            await asyncio.sleep(0.15)
            await self._broadcast_state()

            return result

    def _start_polling(self) -> None:
        """Start background polling for state changes."""
        self._stop_polling()
        self._polling_task = asyncio.create_task(self._poll_loop())

    def _stop_polling(self) -> None:
        """Stop background polling."""
        if self._polling_task:
            self._polling_task.cancel()
            self._polling_task = None

    async def _poll_loop(self) -> None:
        """Poll device state periodically."""
        while self.is_connected:
            try:
                await asyncio.sleep(settings.poll_interval)
                if self.is_connected:
                    await self._broadcast_state()
            except asyncio.CancelledError:
                break
            except Exception:
                continue

    async def _broadcast_state(self) -> None:
        """Query current state and broadcast to all subscribers."""
        if not self.is_connected or not self._client:
            return

        try:
            state = await self._client.query_state()
            message = {
                "type": "state",
                "payload": self._format_state(state),
            }
            await self._broadcast(message)
        except Exception as e:
            await self._broadcast({
                "type": "error",
                "payload": {"code": "query_failed", "message": str(e)},
            })

    async def _broadcast_connection(self, connected: bool) -> None:
        """Broadcast connection state change."""
        message = {
            "type": "connection",
            "payload": {
                "connected": connected,
                "device_name": self._device_name,
                "device_address": self._device_address,
            },
        }
        await self._broadcast(message)

    async def _broadcast(self, message: dict) -> None:
        """Send message to all registered callbacks."""
        for callback in self._state_callbacks:
            try:
                await callback(message)
            except Exception:
                pass

    def _format_state(self, state: dict) -> dict:
        """Format state dict for API response."""
        mode_value = state.get("mode", 0)
        try:
            mode_name = Mode(mode_value).name
        except ValueError:
            mode_name = "UNKNOWN"

        color = state.get("color", Color.off())
        return {
            "connected": True,
            "power": state.get("power", False),
            "mode": mode_value,
            "mode_name": mode_name,
            "brightness": state.get("brightness", 0),
            "color": {
                "r": color.r,
                "g": color.g,
                "b": color.b,
                "warm_white": color.warm_white,
                "cool_white": color.cool_white,
            },
            "timestamp": datetime.now().isoformat(),
        }


# Global singleton instance
device_manager = DeviceManager()
