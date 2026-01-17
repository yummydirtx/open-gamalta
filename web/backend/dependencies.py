"""FastAPI dependency injection for the Gamalta web backend."""

from .services.device_manager import device_manager, DeviceManager


def get_device_manager() -> DeviceManager:
    """Get the global DeviceManager singleton."""
    return device_manager
