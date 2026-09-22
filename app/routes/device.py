from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.device_service import register_device
from app.device_config import get_device_code


router = APIRouter(
    prefix="/api/device",
    tags=["device"],
)


class DeviceRegisterRequest(BaseModel):
    device_code: str


@router.post("/register")
async def register(
    data: DeviceRegisterRequest,
):
    device = register_device(
        data.device_code
    )

    if device is None:
        raise HTTPException(
            status_code=401,
            detail="Устройство не зарегистрировано.",
        )

    return {
        "status": "ok",
        "device": {
            "id": device["id"],
            "site_id": device["site_id"],
            "device_code": device["device_code"],
            "name": device["name"],
            "active": device["active"],
            "last_seen": device["last_seen"],
        },
    }


@router.get("/config")
async def get_device_config():

    return {
        "status": "ok",
        "device_code": get_device_code(),
    }

@router.get("/site")
async def get_device_site():

    device_code = get_device_code()

    from app.device_service import get_device_by_code

    device = get_device_by_code(
        device_code
    )

    if device is None:
        raise HTTPException(
            status_code=401,
            detail="Устройство не зарегистрировано.",
        )

    if device["active"] != 1:
        raise HTTPException(
            status_code=403,
            detail="Устройство отключено.",
        )

    return {
        "status": "ok",
        "device": {
            "id": device["id"],
            "device_code": device["device_code"],
            "name": device["name"],
            "site_id": device["site_id"],
        },
    }