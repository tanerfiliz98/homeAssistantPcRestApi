from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.services import sensors as sensor_service

router = APIRouter(prefix="/sensors", tags=["sensors"], dependencies=[Depends(require_api_key)])


@router.get("")
def all_sensors() -> dict:
    return sensor_service.get_all_sensors()


@router.get("/system")
def system() -> dict:
    return sensor_service.get_system_info()


@router.get("/cpu")
def cpu() -> dict:
    return sensor_service.get_cpu()


@router.get("/memory")
def memory() -> dict:
    return sensor_service.get_memory()


@router.get("/disks")
def disks() -> dict:
    return {"disks": sensor_service.get_disks()}


@router.get("/network")
def network() -> dict:
    return sensor_service.get_network()


@router.get("/temperatures")
def temperatures() -> dict:
    return sensor_service.get_temperatures()


@router.get("/battery")
def battery() -> dict:
    return sensor_service.get_battery()
