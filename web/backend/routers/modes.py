"""Mode control API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from gamalta.types import Mode
from gamalta.exceptions import GamaltaError, NotConnectedError

from ..dependencies import get_device_manager
from ..services.device_manager import DeviceManager
from ..models import (
    ModeRequest,
    ModeInfo,
    ModesResponse,
    SuccessResponse,
)

router = APIRouter()

# Mode descriptions
MODE_INFO = {
    Mode.MANUAL: ModeInfo(
        id=Mode.MANUAL,
        name="MANUAL",
        description="Static color mode - set your own color",
        has_schedule=False,
    ),
    Mode.SUNSYNC: ModeInfo(
        id=Mode.SUNSYNC,
        name="SUNSYNC",
        description="Intelligent 24-hour sun simulation cycle",
        has_schedule=True,
    ),
    Mode.CORAL_REEF: ModeInfo(
        id=Mode.CORAL_REEF,
        name="CORAL_REEF",
        description="24-hour coral reef color cycle",
        has_schedule=True,
    ),
    Mode.FISH_BLUE: ModeInfo(
        id=Mode.FISH_BLUE,
        name="FISH_BLUE",
        description="24-hour deep blue cycle for fish",
        has_schedule=True,
    ),
    Mode.WATERWEED: ModeInfo(
        id=Mode.WATERWEED,
        name="WATERWEED",
        description="24-hour plant growth cycle",
        has_schedule=True,
    ),
}


@router.get("", response_model=ModesResponse)
async def list_modes():
    """List available modes."""
    return ModesResponse(modes=list(MODE_INFO.values()))


@router.post("/set", response_model=SuccessResponse)
async def set_mode(
    request: ModeRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Set the operating mode."""
    if not manager.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to device")

    # Parse mode name to Mode enum
    mode_name = request.mode.upper()
    try:
        mode = Mode[mode_name]
    except KeyError:
        valid_modes = ", ".join(m.name for m in Mode)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode '{request.mode}'. Valid modes: {valid_modes}",
        )

    try:
        await manager.set_mode(mode)
        return SuccessResponse()
    except NotConnectedError:
        raise HTTPException(status_code=400, detail="Not connected to device")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))
