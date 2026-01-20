"""Device management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from gamalta.exceptions import DeviceNotFoundError, GamaltaError

from ..dependencies import get_device_manager
from ..services.device_manager import DeviceManager
from ..models import (
    ConnectRequest,
    ConnectResponse,
    ScanResponse,
    StatusResponse,
    SuccessResponse,
    DeviceInfo,
    NameRequest,
    NameResponse,
)

router = APIRouter()


@router.get("/scan", response_model=ScanResponse)
async def scan_devices(
    timeout: float = 5.0,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Scan for Gamalta devices."""
    try:
        devices = await manager.scan(timeout=timeout)
        return ScanResponse(
            devices=[DeviceInfo(address=d["address"], name=d["name"]) for d in devices]
        )
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}")


@router.post("/connect", response_model=ConnectResponse)
async def connect_device(
    request: ConnectRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Connect to a Gamalta device."""
    try:
        name = await manager.connect(address=request.address)
        return ConnectResponse(success=True, device_name=name)
    except DeviceNotFoundError:
        raise HTTPException(status_code=404, detail="No Gamalta device found")
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {e}")


@router.post("/disconnect", response_model=SuccessResponse)
async def disconnect_device(
    manager: DeviceManager = Depends(get_device_manager),
):
    """Disconnect from the current device."""
    await manager.disconnect()
    return SuccessResponse()


@router.get("/status", response_model=StatusResponse)
async def get_status(
    manager: DeviceManager = Depends(get_device_manager),
):
    """Get connection and device status."""
    state = await manager.get_state()
    return StatusResponse(
        connected=manager.is_connected,
        device_name=manager.device_name,
        device_address=manager.device_address,
        state=state if manager.is_connected else None,
    )


@router.get("/name", response_model=NameResponse)
async def get_name(
    manager: DeviceManager = Depends(get_device_manager),
):
    """Get the device name."""
    if not manager.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to device")
    return NameResponse(name=manager.device_name or "Unknown")


@router.put("/name", response_model=SuccessResponse)
async def set_name(
    request: NameRequest,
    manager: DeviceManager = Depends(get_device_manager),
):
    """Set the device name."""
    if not manager.is_connected:
        raise HTTPException(status_code=400, detail="Not connected to device")
    try:
        await manager.set_name(request.name)
        return SuccessResponse()
    except GamaltaError as e:
        raise HTTPException(status_code=500, detail=str(e))
