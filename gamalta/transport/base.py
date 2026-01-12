"""
Abstract Transport Interface

Defines the interface for BLE (and potentially other) transports.
"""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable


class Transport(ABC):
    """
    Abstract base class for device communication transports.
    
    This abstraction allows for:
    - Mock transport for unit testing
    - Alternative transports (e.g., network bridge devices)
    """
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if transport is currently connected."""
        ...
    
    @abstractmethod
    async def connect(self, address: str) -> None:
        """
        Establish connection to a device.
        
        Args:
            address: Device address (format depends on transport type)
            
        Raises:
            ConnectionError: If connection fails
        """
        ...
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close the connection.
        
        Safe to call even if not connected.
        """
        ...
    
    @abstractmethod
    async def write(self, data: bytes) -> None:
        """
        Write data to the device.
        
        Args:
            data: Bytes to send
            
        Raises:
            NotConnectedError: If not connected
            CommandError: If write fails
        """
        ...
    
    @abstractmethod
    async def subscribe(
        self, 
        callback: Callable[[bytes], None] | Callable[[bytes], Awaitable[None]] | None
    ) -> None:
        """
        Subscribe to notifications from the device.
        
        Args:
            callback: Function to call with received data, or None to unsubscribe
        """
        ...
