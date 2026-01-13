"""
Gamalta - Open source controller for Gamalta Bluetooth smart lights.

Example:
    from gamalta import GamaltaClient, Color, Mode
    
    async def main():
        async with GamaltaClient() as light:
            await light.set_color(255, 100, 0)
            await light.set_brightness(75)
"""

from .client import GamaltaClient
from .types import Color, LightningConfig, Mode, Day
from .exceptions import (
    GamaltaError,
    ConnectionError,
    DeviceNotFoundError,
    AuthenticationError,
    CommandError,
    NotConnectedError,
)
from .transport.ble import scan_for_devices, find_device
from .scenes import (
    Scene,
    SceneKeyframe,
    SceneRegistry,
    get_scene,
    get_scene_registry,
    register_custom_scene,
)

__version__ = "0.1.0"

__all__ = [
    # Main client
    "GamaltaClient",
    # Types
    "Color",
    "LightningConfig", 
    "Mode",
    "Day",
    # Scenes
    "Scene",
    "SceneKeyframe",
    "SceneRegistry",
    "get_scene",
    "get_scene_registry",
    "register_custom_scene",
    # Exceptions
    "GamaltaError",
    "ConnectionError",
    "DeviceNotFoundError",
    "AuthenticationError",
    "CommandError",
    "NotConnectedError",
    # Discovery
    "scan_for_devices",
    "find_device",
]
