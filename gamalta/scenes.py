"""
Scene Interpolation System

Provides 24-hour scene schedules with keyframe-based color/brightness interpolation.
This module allows defining built-in scenes (Fish Blue, Coral Reef, etc.) and 
supports custom user-defined scenes.

The interpolation matches the official app's behavior by calculating the current
color and brightness based on the time of day and applying it before mode switches.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Dict, List, Optional
from enum import IntEnum

from .types import Color, Mode


@dataclass
class SceneKeyframe:
    """
    A keyframe in a 24-hour scene schedule.
    
    Attributes:
        hour: Hour of day (0-23)
        minute: Minute (0-59)
        r, g, b: RGB color values (0-255)
        cool_white: Cool white LED value (0-255)
        warm_white: Warm white LED value (0-255)
        brightness: Master brightness percentage (0-100)
    """
    hour: int
    minute: int = 0
    r: int = 0
    g: int = 0
    b: int = 0
    cool_white: int = 0
    warm_white: int = 0
    brightness: int = 100
    
    @property
    def time_minutes(self) -> int:
        """Time as minutes from midnight (0-1439)."""
        return self.hour * 60 + self.minute
    
    @property
    def color(self) -> Color:
        """Get Color object from this keyframe."""
        return Color(self.r, self.g, self.b, self.warm_white, self.cool_white)
    
    def __repr__(self) -> str:
        return (f"Keyframe({self.hour:02d}:{self.minute:02d} "
                f"RGB({self.r},{self.g},{self.b}) C={self.cool_white} W={self.warm_white} "
                f"Bright={self.brightness}%)")


@dataclass
class Scene:
    """
    A 24-hour scene schedule with keyframes.
    
    Scenes define color and brightness keyframes throughout the day.
    The interpolation function calculates smooth transitions between keyframes.
    """
    name: str
    mode_id: int
    keyframes: List[SceneKeyframe] = field(default_factory=list)
    
    def __post_init__(self):
        # Sort keyframes by time
        self.keyframes = sorted(self.keyframes, key=lambda k: k.time_minutes)
    
    def get_interpolated_state(
        self, 
        current_time: Optional[datetime] = None
    ) -> tuple[Color, int]:
        """
        Calculate the interpolated color and brightness for a given time.
        
        Args:
            current_time: Time to calculate for (default: now)
            
        Returns:
            Tuple of (Color, brightness_percent)
        """
        if current_time is None:
            current_time = datetime.now()
        
        if not self.keyframes:
            return Color.off(), 0
        
        # Convert to minutes since midnight
        now_minutes = current_time.hour * 60 + current_time.minute
        
        # Find surrounding keyframes
        prev_kf = self.keyframes[-1]  # Wrap around from end of day
        next_kf = self.keyframes[0]   # Wrap around to start of day
        
        for i, kf in enumerate(self.keyframes):
            if kf.time_minutes <= now_minutes:
                prev_kf = kf
                next_kf = self.keyframes[(i + 1) % len(self.keyframes)]
            else:
                next_kf = kf
                break
        
        # Handle wrap-around midnight
        prev_time = prev_kf.time_minutes
        next_time = next_kf.time_minutes
        
        if next_time <= prev_time:
            # Crosses midnight
            next_time += 24 * 60
            if now_minutes < prev_time:
                now_minutes += 24 * 60
        
        # Calculate interpolation factor (0.0 to 1.0)
        if next_time == prev_time:
            t = 0.0
        else:
            t = (now_minutes - prev_time) / (next_time - prev_time)
            t = max(0.0, min(1.0, t))
        
        # Linear interpolation
        def lerp(a: int, b: int) -> int:
            return int(round(a + (b - a) * t))
        
        color = Color(
            r=lerp(prev_kf.r, next_kf.r),
            g=lerp(prev_kf.g, next_kf.g),
            b=lerp(prev_kf.b, next_kf.b),
            warm_white=lerp(prev_kf.warm_white, next_kf.warm_white),
            cool_white=lerp(prev_kf.cool_white, next_kf.cool_white),
        )
        brightness = lerp(prev_kf.brightness, next_kf.brightness)
        
        return color, brightness


# =============================================================================
# Built-in Scene Definitions
# =============================================================================

# Fish Blue scene data (collected from official app BLE logs)
FISH_BLUE_KEYFRAMES = [
    SceneKeyframe(hour=5, minute=20, r=0, g=0, b=0, cool_white=234, warm_white=70, brightness=46),
    SceneKeyframe(hour=6, minute=0, r=0, g=0, b=0, cool_white=255, warm_white=76, brightness=50),
    SceneKeyframe(hour=8, minute=0, r=0, g=0, b=0, cool_white=255, warm_white=76, brightness=75),
    SceneKeyframe(hour=9, minute=0, r=64, g=64, b=64, cool_white=255, warm_white=38, brightness=75),
    SceneKeyframe(hour=10, minute=0, r=127, g=127, b=127, cool_white=255, warm_white=0, brightness=75),
    SceneKeyframe(hour=11, minute=0, r=191, g=191, b=191, cool_white=255, warm_white=0, brightness=88),
    SceneKeyframe(hour=12, minute=0, r=255, g=255, b=255, cool_white=255, warm_white=0, brightness=100),
    SceneKeyframe(hour=13, minute=0, r=255, g=255, b=255, cool_white=255, warm_white=128, brightness=100),
    SceneKeyframe(hour=14, minute=0, r=255, g=255, b=255, cool_white=255, warm_white=255, brightness=100),
    SceneKeyframe(hour=15, minute=0, r=191, g=191, b=255, cool_white=191, warm_white=255, brightness=85),
    SceneKeyframe(hour=16, minute=0, r=127, g=127, b=255, cool_white=127, warm_white=255, brightness=70),
    SceneKeyframe(hour=17, minute=0, r=127, g=89, b=191, cool_white=64, warm_white=191, brightness=50),
    SceneKeyframe(hour=18, minute=0, r=127, g=51, b=127, cool_white=0, warm_white=127, brightness=30),
    SceneKeyframe(hour=18, minute=15, r=118, g=43, b=126, cool_white=0, warm_white=118, brightness=24),
    SceneKeyframe(hour=19, minute=0, r=89, g=26, b=127, cool_white=0, warm_white=89, brightness=20),
    SceneKeyframe(hour=20, minute=0, r=51, g=0, b=127, cool_white=0, warm_white=51, brightness=10),
    SceneKeyframe(hour=21, minute=0, r=26, g=0, b=64, cool_white=0, warm_white=26, brightness=5),
    SceneKeyframe(hour=22, minute=0, r=0, g=0, b=0, cool_white=0, warm_white=0, brightness=0),
]

# =============================================================================
# Scene Registry
# =============================================================================

class SceneRegistry:
    """
    Registry for built-in and custom scenes.
    
    Built-in scenes are registered automatically. Custom scenes can be
    added at runtime for Basic and Pro mode customizations.
    """
    
    def __init__(self):
        self._scenes: Dict[int, Scene] = {}
        self._register_builtin_scenes()
    
    def _register_builtin_scenes(self):
        """Register built-in scene definitions."""
        # Fish Blue (0x03)
        self.register(Scene(
            name="Fish Blue",
            mode_id=0x03,
            keyframes=FISH_BLUE_KEYFRAMES,
        ))
        
        # TODO: Add other built-in scenes when data is collected
        # - SunSync (0x01)
        # - Coral Reef (0x02)
        # - Waterweed (0x04)
    
    def register(self, scene: Scene) -> None:
        """Register a scene."""
        self._scenes[scene.mode_id] = scene
    
    def get(self, mode_id: int) -> Optional[Scene]:
        """Get a scene by mode ID."""
        return self._scenes.get(mode_id)
    
    def has(self, mode_id: int) -> bool:
        """Check if a scene is registered."""
        return mode_id in self._scenes
    
    def unregister(self, mode_id: int) -> None:
        """Remove a registered scene."""
        self._scenes.pop(mode_id, None)
    
    def list_scenes(self) -> List[Scene]:
        """List all registered scenes."""
        return list(self._scenes.values())


# Global scene registry instance
_registry = SceneRegistry()


def get_scene_registry() -> SceneRegistry:
    """Get the global scene registry."""
    return _registry


def get_scene(mode_id: int) -> Optional[Scene]:
    """Get a scene by mode ID from the global registry."""
    return _registry.get(mode_id)


def register_custom_scene(
    name: str,
    mode_id: int,
    keyframes: List[SceneKeyframe]
) -> Scene:
    """
    Register a custom scene.
    
    Use this for Basic (0x0B) and Pro (0x0C) mode customizations.
    
    Args:
        name: Human-readable scene name
        mode_id: Mode ID (e.g., 0x0B for Basic, 0x0C for Pro)
        keyframes: List of SceneKeyframe objects defining the schedule
        
    Returns:
        The registered Scene object
    """
    scene = Scene(name=name, mode_id=mode_id, keyframes=keyframes)
    _registry.register(scene)
    return scene
