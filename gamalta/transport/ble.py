"""
BLE Transport Implementation

Bleak-based Bluetooth Low Energy transport for Gamalta devices.
"""

import asyncio
from typing import Callable, Awaitable

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from .base import Transport
from ..protocol.constants import CHAR_WRITE_UUID, CHAR_NOTIFY_UUID
from ..exceptions import ConnectionError, DeviceNotFoundError, NotConnectedError, CommandError


async def scan_for_devices(
    name_filter: str = "Gamalta",
    timeout: float = 5.0
) -> list[BLEDevice]:
    """
    Scan for Gamalta devices.
    
    Args:
        name_filter: String that must appear in device name
        timeout: Scan duration in seconds
        
    Returns:
        List of discovered BLE devices matching the filter
    """
    devices = await BleakScanner.discover(timeout=timeout)
    return [
        d for d in devices 
        if d.name and name_filter in d.name
    ]


async def find_device(
    name_filter: str = "Gamalta",
    timeout: float = 5.0
) -> BLEDevice:
    """
    Find a single Gamalta device.
    
    Args:
        name_filter: String that must appear in device name
        timeout: Scan duration in seconds
        
    Returns:
        First matching BLE device
        
    Raises:
        DeviceNotFoundError: If no matching device found
    """
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name is not None and name_filter in d.name,
        timeout=timeout
    )
    
    if device is None:
        raise DeviceNotFoundError(
            f"No device found matching '{name_filter}'. "
            "Ensure the light is powered on and not connected to another app."
        )
    
    return device


class BleTransport(Transport):
    """
    Bluetooth Low Energy transport using Bleak.
    
    This is the primary transport for communicating with Gamalta devices.
    """
    
    def __init__(self):
        self._client: BleakClient | None = None
        self._address: str | None = None
        self._notify_callback: Callable[[bytes], None] | None = None
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected to a device."""
        return self._client is not None and self._client.is_connected
    
    @property
    def address(self) -> str | None:
        """The address of the connected device, or None if not connected."""
        return self._address
    
    async def connect(self, address: str) -> None:
        """
        Connect to a device by address.
        
        Args:
            address: BLE device address (MAC on Linux, UUID on macOS)
            
        Raises:
            ConnectionError: If connection fails
        """
        if self.is_connected:
            await self.disconnect()
        
        try:
            self._client = BleakClient(address)
            await self._client.connect()
            self._address = address
        except BleakError as e:
            self._client = None
            self._address = None
            raise ConnectionError(f"Failed to connect to {address}: {e}") from e
    
    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client is not None:
            try:
                if self._client.is_connected:
                    await self._client.disconnect()
            except BleakError:
                pass  # Ignore disconnect errors
            finally:
                self._client = None
                self._address = None
    
    async def write(self, data: bytes) -> None:
        """
        Write data to the device's write characteristic.
        
        Args:
            data: Bytes to send
            
        Raises:
            NotConnectedError: If not connected
            CommandError: If write fails
        """
        if not self.is_connected or self._client is None:
            raise NotConnectedError("Not connected to device")
        
        try:
            await self._client.write_gatt_char(
                CHAR_WRITE_UUID, 
                data, 
                response=False
            )
        except BleakError as e:
            raise CommandError(f"Write failed: {e}") from e
    
    async def subscribe(
        self,
        callback: Callable[[bytes], None] | Callable[[bytes], Awaitable[None]] | None
    ) -> None:
        """
        Subscribe to notifications from the device.
        
        Args:
            callback: Function to call with received data, or None to unsubscribe
            
        Raises:
            NotConnectedError: If not connected
        """
        if not self.is_connected or self._client is None:
            raise NotConnectedError("Not connected to device")
        
        if callback is None:
            # Unsubscribe
            try:
                await self._client.stop_notify(CHAR_NOTIFY_UUID)
            except BleakError:
                pass
            self._notify_callback = None
        else:
            # Subscribe with wrapper to handle the bleak callback signature
            def _wrapper(sender: int, data: bytearray):
                if self._notify_callback:
                    result = self._notify_callback(bytes(data))
                    if asyncio.iscoroutine(result):
                        asyncio.create_task(result)
            
            self._notify_callback = callback
            await self._client.start_notify(CHAR_NOTIFY_UUID, _wrapper)
    
    async def __aenter__(self) -> "BleTransport":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensures disconnection."""
        await self.disconnect()
