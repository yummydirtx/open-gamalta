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
from .scenes import get_scene


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
        """Perform the login, time sync, and scene activation handshake."""
        # Login with default password
        await self._send(commands.build_login())
        
        # Sync time
        await self._send(commands.build_time_sync())
        
        # Scene activate - required to keep current scene state intact
        # Without this, the device may reset to a default state
        await self._send(commands.build_scene_activate())
    
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
    
    async def set_rgb(self, r: int, g: int, b: int) -> None:
        """
        Set only the RGB channels, preserving warm/cool white values.
        
        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
        """
        state = await self.query_state()
        color = state["color"]
        await self._send(commands.build_color(Color(
            r, g, b, color.warm_white, color.cool_white
        )))
    
    async def set_warm_white(self, level: int) -> None:
        """
        Set only the warm white channel, preserving all other values.
        
        Args:
            level: Warm white brightness (0-255)
        """
        state = await self.query_state()
        color = state["color"]
        await self._send(commands.build_color(Color(
            color.r, color.g, color.b, level, color.cool_white
        )))
    
    async def set_cool_white(self, level: int) -> None:
        """
        Set only the cool white channel, preserving all other values.
        
        Args:
            level: Cool white brightness (0-255)
        """
        state = await self.query_state()
        color = state["color"]
        await self._send(commands.build_color(Color(
            color.r, color.g, color.b, color.warm_white, level
        )))
    
    async def set_red(self, level: int) -> None:
        """
        Set only the red channel, preserving all other values.
        
        Args:
            level: Red brightness (0-255)
        """
        state = await self.query_state()
        color = state["color"]
        await self._send(commands.build_color(Color(
            level, color.g, color.b, color.warm_white, color.cool_white
        )))
    
    async def set_green(self, level: int) -> None:
        """
        Set only the green channel, preserving all other values.
        
        Args:
            level: Green brightness (0-255)
        """
        state = await self.query_state()
        color = state["color"]
        await self._send(commands.build_color(Color(
            color.r, level, color.b, color.warm_white, color.cool_white
        )))
    
    async def set_blue(self, level: int) -> None:
        """
        Set only the blue channel, preserving all other values.
        
        Args:
            level: Blue brightness (0-255)
        """
        state = await self.query_state()
        color = state["color"]
        await self._send(commands.build_color(Color(
            color.r, color.g, level, color.warm_white, color.cool_white
        )))
    
    async def set_rgbwc(
        self, 
        r: int, 
        g: int, 
        b: int, 
        warm_white: int, 
        cool_white: int
    ) -> None:
        """
        Set all color channels at once (RGB + warm/cool white).
        
        This is the low-level method that sets all channels without
        querying state or sending mode commands.
        
        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            warm_white: Warm white LED (0-255)
            cool_white: Cool white LED (0-255)
        """
        await self._send(commands.build_color(Color(
            r, g, b, warm_white, cool_white
        )))
    
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
    
    async def set_mode(self, mode: Mode | int, apply_scene_color: bool = True) -> None:
        """
        Set the operating mode/scene.
        
        For 24h cycle modes (Fish Blue, Coral Reef, etc.), this will:
        1. Look up the scene's keyframe schedule
        2. Calculate the current interpolated color/brightness
        3. Apply the color and brightness before switching mode
        4. Send the mode command and scene activate
        
        This matches the official app's behavior for immediate visual updates.
        
        Args:
            mode: Mode to activate (use Mode enum)
            apply_scene_color: If True, apply interpolated color for known scenes
        """
        mode_int = int(mode)
        
        # For 24h cycle modes, apply interpolated color first
        if mode_int != 0x00 and apply_scene_color:
            scene = get_scene(mode_int)
            if scene:
                color, brightness = scene.get_interpolated_state()
                # Apply color and brightness like the official app
                # Use apply_flag=0x01 for scene activation (vs 0x00 for manual)
                await self._send(commands.build_color(color, apply_flag=0x01))
                await self._send(commands.build_brightness(brightness))
        
        # Send mode command
        await self._send(commands.build_mode(mode_int))
        
        # For 24h cycle modes (not MANUAL), also send scene activate
        # followed by state query to lock in values (matches app behavior)
        if mode_int != 0x00:
            await self._send(commands.build_scene_activate())
            await self._send(commands.build_state_query())
    
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
    # State Query
    # =========================================================================
    
    async def query_state(self, timeout: float = 2.0) -> dict:
        """
        Query the current device state.
        
        Args:
            timeout: Maximum time to wait for response
            
        Returns:
            Dictionary with keys:
            - power: bool (True = on)
            - mode: int (mode ID)
            - brightness: int (0-100)
            - color: Color object (RGBWC values)
            
        Note:
            Color values are LIVE INTERPOLATED for 24h scenes,
            not the static scene definition.
        """
        response_data: bytes | None = None
        response_event = asyncio.Event()
        
        def capture_response(data: bytes) -> None:
            nonlocal response_data
            # Response starts with A5, then seq, then 0x04 (state response)
            if len(data) >= 3 and data[2] == 0x04:
                response_data = data
                response_event.set()
        
        # Temporarily capture the response
        old_callback = self._notify_callback
        self._notify_callback = capture_response
        
        try:
            await self._send(commands.build_state_query())
            await asyncio.wait_for(response_event.wait(), timeout=timeout)
            
            if response_data and len(response_data) >= 12:
                # Parse: [A5] [seq] [04] [08] [power] [mode] [bright] [R] [G] [B] [C] [W]
                return {
                    "power": response_data[4] == 0x01,
                    "mode": response_data[5],
                    "brightness": response_data[6],
                    "color": Color(
                        r=response_data[7],
                        g=response_data[8],
                        b=response_data[9],
                        warm_white=response_data[11],  # W comes after C
                        cool_white=response_data[10],
                    ),
                }
            else:
                return {"power": False, "mode": 0, "brightness": 0, "color": Color.off()}
        except asyncio.TimeoutError:
            return {"power": False, "mode": 0, "brightness": 0, "color": Color.off()}
        finally:
            self._notify_callback = old_callback
    
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

