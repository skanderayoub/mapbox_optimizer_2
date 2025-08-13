from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query
from services.matching_service import matching_service

router = APIRouter(prefix="/match", tags=["matching"])

@router.get("/drivers-for-rider/{rider_id}")
def drivers_for_rider(rider_id: str, on_date: Optional[str] = Query(default=None, description="YYYY-MM-DD")):
    target = datetime.fromisoformat(on_date).date() if on_date else None
    return matching_service.drivers_for_rider(rider_id, target)

@router.get("/riders-for-driver/{driver_id}")
def riders_for_driver(driver_id: str, on_date: Optional[str] = Query(default=None, description="YYYY-MM-DD")):
    target = datetime.fromisoformat(on_date).date() if on_date else None
    return matching_service.riders_for_driver(driver_id, target)