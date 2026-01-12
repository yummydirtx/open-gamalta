"""
Gamalta Client

High-level async API for controlling Gamalta smart lights.
"""

import asyncio
from datetime import datetime
from typing import Callable, Awaitable

from .types import Color, LightningConfig, Mode
from .exceptions import NotConnectedError
from .protocol.packet import PacketBuilder
from .protocol import commands
from .transport.base import Transport
from .transport.ble import BleTransport, find_device


class GamaltaClient:
    """
    High-level client for controlling Gamalta smart lights.
    
    This is the main entry point for the library. It handles:
    - Device discovery and connection
    - Protocol handshake (login + time sync)
    - All light control operations
    
    Example:
        async with GamaltaClient() as light:
            await light.set_color(255, 100, 0)
            await light.set_brightness(75)
    """
    
    # Delay between commands to avoid overwhelming the device
    COMMAND_DELAY = 0.1
    
    def __init__(self, transport: Transport | None = None):
        """
        Initialize the client.
        
        Args:
            transport: Transport to use (defaults to BleTransport)
        """
        self._transport = transport or BleTransport()
        self._packet_builder = PacketBuilder()
        self._connected = False
        self._notify_callback: Callable[[bytes], None] | None = None
    
    @property
    def is_connected(self) -> bool:
        """Check if connected and authenticated with a device."""
        return self._connected and self._transport.is_connected
    
    async def connect(
        self,
        address: str | None = None,
        name_filter: str = "Gamalta",
        timeout: float = 5.0
    ) -> None:
        """
        Connect to a Gamalta device.
        
        If no address is provided, scans for devices matching the name filter.
        
        Args:
            address: Specific device address, or None to auto-discover
            name_filter: Name filter for auto-discovery
            timeout: Scan timeout in seconds
            
        Raises:
            DeviceNotFoundError: If no device found during auto-discovery
            ConnectionError: If connection fails
        """
        # Auto-discover if no address provided
        if address is None:
            device = await find_device(name_filter, timeout)
            address = device.address
        
        # Connect transport
        await self._transport.connect(address)
        
        # Subscribe to notifications
        await self._transport.subscribe(self._on_notify)
        await asyncio.sleep(0.2)
        
        # Perform handshake
        await self._handshake()
        self._connected = True
    
    async def disconnect(self) -> None:
        """Disconnect from the device."""
        self._connected = False
        await self._transport.disconnect()
    
    async def _send(self, payload: bytes) -> None:
        """Send a command payload (header and sequence added automatically)."""
        if not self._transport.is_connected:
            raise NotConnectedError("Not connected to device")
        
        packet = self._packet_builder.build(payload)
        await self._transport.write(packet)
        await asyncio.sleep(self.COMMAND_DELAY)
    
    async def _handshake(self) -> None:
        """Perform the login and time sync handshake."""
        # Login with default password
        await self._send(commands.build_login())
        
        # Sync time
        await self._send(commands.build_time_sync())
    
    def _on_notify(self, data: bytes) -> None:
        """Handle notification data from device."""
        if self._notify_callback:
            self._notify_callback(data)
    
    def on_notify(
        self, 
        callback: Callable[[bytes], None] | None
    ) -> None:
        """
        Set a callback for device notifications.
        
        Args:
            callback: Function to call with notification data, or None to clear
        """
        self._notify_callback = callback
    
    # =========================================================================
    # Power Control
    # =========================================================================
    
    async def power_on(self) -> None:
        """Turn the light on."""
        await self._send(commands.build_power(True))
    
    async def power_off(self) -> None:
        """Turn the light off."""
        await self._send(commands.build_power(False))
    
    # =========================================================================
    # Color Control
    # =========================================================================
    
    async def set_color(
        self, 
        r: int, 
        g: int, 
        b: int, 
        warm_white: int = 0, 
        cool_white: int = 0,
        set_manual_mode: bool = True
    ) -> None:
        """
        Set the light color.
        
        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            warm_white: Warm white LED (0-255)
            cool_white: Cool white LED (0-255)
            set_manual_mode: Also switch to manual mode (recommended)
        """
        color = Color(r, g, b, warm_white, cool_white)
        await self._send(commands.build_color(color))
        
        if set_manual_mode:
            await self.set_mode(Mode.MANUAL)
    
    async def set_color_obj(self, color: Color, set_manual_mode: bool = True) -> None:
        """
        Set the light color using a Color object.
        
        Args:
            color: Color to set
            set_manual_mode: Also switch to manual mode (recommended)
        """
        await self._send(commands.build_color(color))
        
        if set_manual_mode:
            await self.set_mode(Mode.MANUAL)
    
    # =========================================================================
    # Brightness Control
    # =========================================================================
    
    async def set_brightness(self, percent: int) -> None:
        """
        Set the master brightness level.
        
        Args:
            percent: Brightness 0-100
        """
        await self._send(commands.build_brightness(percent))
    
    # =========================================================================
    # Mode Control
    # =========================================================================
    
    async def set_mode(self, mode: Mode | int) -> None:
        """
        Set the operating mode/scene.
        
        Args:
            mode: Mode to activate (use Mode enum)
        """
        await self._send(commands.build_mode(int(mode)))
    
    # =========================================================================
    # Lightning Effects
    # =========================================================================
    
    async def configure_lightning(self, config: LightningConfig) -> None:
        """
        Configure the automatic lightning storm effect.
        
        Args:
            config: Lightning configuration
        """
        await self._send(commands.build_lightning(config))
    
    async def preview_lightning(self) -> None:
        """Trigger a single lightning flash preview."""
        await self._send(commands.build_lightning_preview())
    
    # =========================================================================
    # Context Manager Support
    # =========================================================================
    
    async def __aenter__(self) -> "GamaltaClient":
        """Context manager entry - connects to device."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - disconnects from device."""
        await self.disconnect()
