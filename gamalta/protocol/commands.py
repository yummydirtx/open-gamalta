"""
Gamalta Command Builders

Functions to build protocol command payloads for all supported operations.
"""

from datetime import datetime
from ..types import Color, LightningConfig
from .constants import (
    CMD_LOGIN, CMD_TIME_SYNC, CMD_POWER, CMD_COLOR,
    CMD_BRIGHTNESS, CMD_MODE, CMD_LIGHTNING,
    CMD_STATE_QUERY, CMD_SCENE_ACTIVATE,
    POWER_ON, POWER_OFF, LIGHTNING_MASK, DEFAULT_PASSWORD
)


def build_login(password: str = DEFAULT_PASSWORD) -> bytes:
    """
    Build the login/authentication command payload.
    
    Args:
        password: Device password (default: "123456")
        
    Returns:
        Command payload bytes (without header/sequence)
    """
    # Command structure: [CMD] [LEN] [0x02] [password as ASCII]
    password_bytes = password.encode('ascii')
    return bytes([CMD_LOGIN, len(password_bytes) + 1, 0x02]) + password_bytes


def build_time_sync(dt: datetime | None = None) -> bytes:
    """
    Build the time synchronization command payload.
    
    Args:
        dt: Datetime to sync (defaults to current time)
        
    Returns:
        Command payload bytes
    """
    if dt is None:
        dt = datetime.now()
    
    # Year is offset from 2000
    year = dt.year - 2000
    
    return bytes([
        CMD_TIME_SYNC, 0x07,
        year, dt.month, dt.day,
        dt.hour, dt.minute, dt.second
    ])


def build_power(on: bool) -> bytes:
    """
    Build the power on/off command payload.
    
    Args:
        on: True for power on, False for power off
        
    Returns:
        Command payload bytes
    """
    state = POWER_ON if on else POWER_OFF
    return bytes([CMD_POWER, 0x03, state, 0x00, 0x00])


def build_color(color: Color, apply_flag: int = 0x00) -> bytes:
    """
    Build the direct color control command payload.
    
    Args:
        color: Color to set (RGBWC)
        apply_flag: 0x00 for manual color changes, 0x01 for scene activation
        
    Returns:
        Command payload bytes
    """
    return bytes([
        CMD_COLOR, 0x06,
        color.r, color.g, color.b,
        color.cool_white, color.warm_white,  # Protocol order: R G B C W
        apply_flag
    ])


def build_color_rgb(r: int, g: int, b: int, w: int = 0, c: int = 0) -> bytes:
    """
    Build the direct color control command from RGB values.
    
    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)
        w: Warm white (0-255)
        c: Cool white (0-255)
        
    Returns:
        Command payload bytes
    """
    return build_color(Color(r, g, b, w, c))


def build_brightness(percent: int) -> bytes:
    """
    Build the master brightness command payload.
    
    Args:
        percent: Brightness level 0-100
        
    Returns:
        Command payload bytes
        
    Raises:
        ValueError: If percent is out of range
    """
    if not 0 <= percent <= 100:
        raise ValueError(f"brightness must be 0-100, got {percent}")
    
    return bytes([CMD_BRIGHTNESS, 0x01, percent])


def build_mode(mode: int) -> bytes:
    """
    Build the mode/scene selection command payload.
    
    Args:
        mode: Mode ID (use Mode enum or constants)
        
    Returns:
        Command payload bytes
    """
    return bytes([CMD_MODE, 0x01, mode])


def build_lightning(config: LightningConfig) -> bytes:
    """
    Build the lightning effect configuration command payload.
    
    Args:
        config: Lightning configuration
        
    Returns:
        Command payload bytes
    """
    return bytes([
        CMD_LIGHTNING, LIGHTNING_MASK,
        config.intensity,
        config.frequency,
        config.start_time.hour,
        config.start_time.minute,
        config.end_time.hour,
        config.end_time.minute,
        config.days_byte
    ])


def build_lightning_preview() -> bytes:
    """
    Build a lightning preview command (triggers single flash).
    
    Returns:
        Command payload bytes
    """
    return build_lightning(LightningConfig.preview())


def build_state_query() -> bytes:
    """
    Build the state query command payload.
    
    Response format: [04] [08] [power] [mode] [brightness] [R] [G] [B] [C] [W]
    
    Returns:
        Command payload bytes
    """
    return bytes([CMD_STATE_QUERY, 0x00])


def build_scene_activate() -> bytes:
    """
    Build the scene activation command payload.
    
    Called after mode selection to activate the scene.
    
    Returns:
        Command payload bytes
    """
    return bytes([CMD_SCENE_ACTIVATE, 0x01, 0x00])
