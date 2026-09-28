from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


class UpdateSettingsRequest(BaseModel):
    settings: Dict[str, Any]


@router.get(
    "",
    summary="Get laboratory system settings (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def get_settings(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "settings",
        "labId": current_user.labId,
        "settings": {
            "currency": "INR",
            "timezone": "Asia/Kolkata",
            "reportHeaderEnabled": True,
            "autoVerificationEnabled": False,
        },
    }


@router.put(
    "",
    summary="Update laboratory settings (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def update_settings(
    data: UpdateSettingsRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Settings updated successfully",
        "module": "settings",
        "labId": current_user.labId,
        "updatedSettings": data.settings,
        "updatedBy": current_user.userId,
    }
