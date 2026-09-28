from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/lab-profile", tags=["Lab Profile"])


class UpdateLabProfileRequest(BaseModel):
    labName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    accreditationNumber: Optional[str] = None


@router.get(
    "",
    summary="Get laboratory profile (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def get_lab_profile(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "lab-profile",
        "labId": current_user.labId,
        "labName": current_user.labName,
        "profile": {
            "accredited": True,
            "status": "active",
        },
    }


@router.put(
    "",
    summary="Update laboratory profile (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def update_lab_profile(
    data: UpdateLabProfileRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Laboratory profile updated successfully",
        "module": "lab-profile",
        "labId": current_user.labId,
        "updatedBy": current_user.userId,
    }
