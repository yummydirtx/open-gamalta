"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field


# Request models

class ConnectRequest(BaseModel):
    """Request to connect to a device."""
    address: str | None = Field(default=None, description="BLE address (auto-discover if not provided)")


class PowerRequest(BaseModel):
    """Request to set power state."""
    on: bool = Field(description="True to turn on, False to turn off")


class ColorRequest(BaseModel):
    """Request to set color."""
    r: int = Field(ge=0, le=255, description="Red channel (0-255)")
    g: int = Field(ge=0, le=255, description="Green channel (0-255)")
    b: int = Field(ge=0, le=255, description="Blue channel (0-255)")
    warm_white: int = Field(default=0, ge=0, le=255, description="Warm white channel (0-255)")
    cool_white: int = Field(default=0, ge=0, le=255, description="Cool white channel (0-255)")


class BrightnessRequest(BaseModel):
    """Request to set brightness."""
    percent: int = Field(ge=0, le=100, description="Brightness (0-100)")


class ModeRequest(BaseModel):
    """Request to set mode."""
    mode: str = Field(description="Mode name: MANUAL, SUNSYNC, CORAL_REEF, FISH_BLUE, WATERWEED")


class LightningRequest(BaseModel):
    """Request to configure lightning effect."""
    intensity: int = Field(ge=0, le=100, description="Flash intensity (0-100)")
    frequency: int = Field(ge=0, le=10, description="Flashes per interval (0-10)")
    start_hour: int = Field(ge=0, le=23, description="Start hour")
    start_minute: int = Field(ge=0, le=59, description="Start minute")
    end_hour: int = Field(ge=0, le=23, description="End hour")
    end_minute: int = Field(ge=0, le=59, description="End minute")
    days: list[str] = Field(description="Days: monday, tuesday, wednesday, thursday, friday, saturday, sunday")
    enabled: bool = Field(default=True, description="Enable lightning schedule")


class NameRequest(BaseModel):
    """Request to set device name."""
    name: str = Field(min_length=1, max_length=16, description="Device name (1-16 characters)")


# Response models

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True


class DeviceInfo(BaseModel):
    """Device information from scan."""
    address: str
    name: str


class ScanResponse(BaseModel):
    """Response from device scan."""
    devices: list[DeviceInfo]


class ConnectResponse(BaseModel):
    """Response from connect."""
    success: bool
    device_name: str | None = None


class ColorInfo(BaseModel):
    """Color information."""
    r: int
    g: int
    b: int
    warm_white: int
    cool_white: int


class DeviceState(BaseModel):
    """Full device state."""
    connected: bool
    power: bool
    mode: int
    mode_name: str
    brightness: int
    color: ColorInfo
    timestamp: str | None = None


class StatusResponse(BaseModel):
    """Response from status endpoint."""
    connected: bool
    device_name: str | None
    device_address: str | None
    state: DeviceState | None


class ModeInfo(BaseModel):
    """Information about a mode."""
    id: int
    name: str
    description: str
    has_schedule: bool


class ModesResponse(BaseModel):
    """Response with available modes."""
    modes: list[ModeInfo]


class NameResponse(BaseModel):
    """Response with device name."""
    name: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str | None = None
