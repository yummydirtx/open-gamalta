"""
Gamalta Data Types

Type-safe data classes for protocol parameters.
"""

from dataclasses import dataclass, field
from datetime import time
from enum import IntEnum


class Mode(IntEnum):
    """Operating modes for the light."""
    MANUAL = 0x00      # Static color mode
    SUNSYNC = 0x01     # Intelligent SunSync - 24h cycle
    CORAL_REEF = 0x02  # 24h cycle - coral reef colors
    FISH_BLUE = 0x03   # 24h cycle - deep blue
    WATERWEED = 0x04   # 24h cycle - plant growth


class Day(IntEnum):
    """Day bitmask values for scheduling."""
    MONDAY = 0x01
    TUESDAY = 0x02
    WEDNESDAY = 0x04
    THURSDAY = 0x08
    FRIDAY = 0x10
    SATURDAY = 0x20
    SUNDAY = 0x40


@dataclass(frozen=True, slots=True)
class Color:
    """
    RGBWC color value for the light.
    
    All values are 0-255.
    
    Attributes:
        r: Red channel
        g: Green channel
        b: Blue channel
        warm_white: Warm white LED channel
        cool_white: Cool white LED channel
    """
    r: int
    g: int
    b: int
    warm_white: int = 0
    cool_white: int = 0
    
    def __post_init__(self):
        for name, value in [
            ('r', self.r), ('g', self.g), ('b', self.b),
            ('warm_white', self.warm_white), ('cool_white', self.cool_white)
        ]:
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be 0-255, got {value}")
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        """Create a color with RGB only (no white channels)."""
        return cls(r, g, b, 0, 0)
    
    @classmethod
    def white(cls, warm: int = 0, cool: int = 255) -> "Color":
        """Create a white color using the white LED channels."""
        return cls(0, 0, 0, warm, cool)
    
    # Common preset colors
    @classmethod
    def red(cls) -> "Color":
        return cls(255, 0, 0)
    
    @classmethod
    def green(cls) -> "Color":
        return cls(0, 255, 0)
    
    @classmethod
    def blue(cls) -> "Color":
        return cls(0, 0, 255)
    
    @classmethod
    def off(cls) -> "Color":
        return cls(0, 0, 0, 0, 0)


@dataclass(frozen=True, slots=True)
class LightningConfig:
    """
    Configuration for the automatic lightning storm effect.
    
    Attributes:
        intensity: Flash intensity 0-100 (percent)
        frequency: Flashes per interval 0-10
        start_time: Start time of the schedule
        end_time: End time of the schedule
        days: Bitmask of days (use Day enum values OR'd together)
        enabled: Master enable switch
    """
    intensity: int
    frequency: int
    start_time: time
    end_time: time
    days: int = 0x7F  # All days by default
    enabled: bool = True
    
    def __post_init__(self):
        if not 0 <= self.intensity <= 100:
            raise ValueError(f"intensity must be 0-100, got {self.intensity}")
        if not 0 <= self.frequency <= 10:
            raise ValueError(f"frequency must be 0-10, got {self.frequency}")
        if not 0 <= self.days <= 0x7F:
            raise ValueError(f"days bitmask must be 0-127, got {self.days}")
    
    @property
    def days_byte(self) -> int:
        """Get the full days byte including enable bit."""
        if self.enabled:
            return self.days | 0x80
        return self.days
    
    @classmethod
    def preview(cls) -> "LightningConfig":
        """
        Create a config that triggers immediate preview mode.
        
        The device will flash once when this is sent.
        """
        return cls(
            intensity=0xFE,  # Special preview value
            frequency=5,
            start_time=time(0, 0),
            end_time=time(0, 0),
            days=0,
            enabled=False
        )
