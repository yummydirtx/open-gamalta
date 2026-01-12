"""
Gamalta Exception Hierarchy

Custom exceptions for error handling.
"""


class GamaltaError(Exception):
    """Base exception for all Gamalta-related errors."""
    pass


class ConnectionError(GamaltaError):
    """Failed to establish or maintain BLE connection."""
    pass


class DeviceNotFoundError(GamaltaError):
    """Could not discover a Gamalta device during scanning."""
    pass


class AuthenticationError(GamaltaError):
    """Handshake/login sequence failed."""
    pass


class CommandError(GamaltaError):
    """A command was rejected or failed to execute."""
    pass


class NotConnectedError(GamaltaError):
    """Attempted to send a command without an active connection."""
    pass
