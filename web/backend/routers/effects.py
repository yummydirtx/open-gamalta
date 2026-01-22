"""Effects API endpoints (lightning)."""

from datetime import time

from fastapi import APIRouter, Depends, HTTPException

from gamalta.types import LightningConfig, Day
from gamalta.exceptions import GamaltaError, NotConnectedError

from ..dependencies import get_device_manager
from ..services.device_manager import DeviceManager
from ..models import (
    LightningRequest,
    SuccessResponse,
)

router = APIRouter()

# Day name to Day enum mapping
DAY_MAP = {
    "monday": Day.MONDAY,
    "tuesday": Day.TUESDAY,
    "wednesday": Day.WEDNESDAY,
    "thursday": Day.THURSDAY,
    "friday": Day.FRIDAY,
    "saturday": Day.SATURDAY,
    "sunday": Day.SUNDAY,
}


def _parse_days(day_names: list[str]) -> int:
    """Convert list of day names to bitmask."""
    bitmask = 0
    for name in day_names:
        name_lower = name.lower()
        if name_lower not in DAY_MAP:
            raise ValueError(f"Invalid day name: {name}")
        bitmask |= DAY_MAP[name_lower]
    return bitmask


@router.post("/lightning/preview", response_model=SuccessResponse)
async def preview_lightning(
    manager: DeviceManager = Depends(get_device_manager),
):
    """Trigger a single lightning flash preview."""
    if not manager.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to device")

    try:
        await manager.preview_lightning()
        return SuccessResponse()
    except NotConnectedError:
        raise HTTPException(status_code=400, detail="Not connected to device")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lightning/configure", response_model=SuccessResponse)
async def configure_lightning(
    request: LightningRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Configure the lightning effect schedule."""
    if not manager.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to device")

    try:
        days_bitmask = _parse_days(request.days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    config = LightningConfig(
        intensity=request.intensity,
        frequency=request.frequency,
        start_time=time(request.start_hour, request.start_minute),
        end_time=time(request.end_hour, request.end_minute),
        days=days_bitmask,
        enabled=request.enabled,
    )

    try:
        await manager.configure_lightning(config)
        return SuccessResponse()
    except NotConnectedError:
        raise HTTPException(status_code=400, detail="Not connected to device")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))
