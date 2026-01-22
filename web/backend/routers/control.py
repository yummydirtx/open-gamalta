"""Light control API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from gamalta.exceptions import GamaltaError, NotConnectedError

from ..dependencies import get_device_manager
from ..services.device_manager import DeviceManager
from ..models import (
    PowerRequest,
    ColorRequest,
    BrightnessRequest,
    SuccessResponse,
)

router = APIRouter()


def _check_connected(manager: DeviceManager):
    """Check if connected to device."""
    if not manager.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to device")


@router.post("/power", response_model=SuccessResponse)
async def set_power(
    request: PowerRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Turn the light on or off."""
    _check_connected(manager)
    try:
        if request.on:
            await manager.power_on()
        else:
            await manager.power_off()
        return SuccessResponse()
    except NotConnectedError:
        raise HTTPException(status_code=400, detail="Not connected to device")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/color", response_model=SuccessResponse)
async def set_color(
    request: ColorRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Set the light color (RGBWC)."""
    _check_connected(manager)
    try:
        await manager.set_color(
            r=request.r,
            g=request.g,
            b=request.b,
            warm_white=request.warm_white,
            cool_white=request.cool_white,
        )
        return SuccessResponse()
    except NotConnectedError:
        raise HTTPException(status_code=400, detail="Not connected to device")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brightness", response_model=SuccessResponse)
async def set_brightness(
    request: BrightnessRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Set the brightness level."""
    _check_connected(manager)
    try:
        await manager.set_brightness(request.percent)
        return SuccessResponse()
    except NotConnectedError:
        raise HTTPException(status_code=400, detail="Not connected to device")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))
