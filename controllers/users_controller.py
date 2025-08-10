from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    home: Optional[List[float]] = Field(default=None, description="[lat, lon]")
    work: Optional[List[float]] = Field(default=None, description="[lat, lon]")
    company: Optional[str] = None
    birthdate: Optional[str] = None
    departement: Optional[str] = None

class UserUpdate(UserCreate):
    pass

@router.post("", summary="Create user")
def create_user(payload: UserCreate):
    user = user_service.create(payload.dict(exclude_unset=True))
    return user.to_dict()

@router.get("/{user_id}", summary="Get user")
def get_user(user_id: str):
    user = user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()

@router.patch("/{user_id}", summary="Update user")
def update_user(user_id: str, payload: UserUpdate):
    try:
        user = user_service.update(user_id, payload.dict(exclude_unset=True))
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))