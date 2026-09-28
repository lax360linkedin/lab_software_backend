from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/staff", tags=["Staff / Users"])


class CreateStaffRequest(BaseModel):
    name: str = Field(..., description="Staff member full name")
    email: EmailStr = Field(..., description="Staff login email")
    phone: str = Field(..., description="Staff contact number")
    role: str = Field(..., description="Assigned role: receptionist or lab_technician")
    password: str = Field(..., min_length=8, description="Initial account password")


@router.get(
    "",
    summary="List laboratory staff / users (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def list_staff(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "staff",
        "labId": current_user.labId,
        "total": 0,
        "staffMembers": [],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create laboratory staff account (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def create_staff_member(
    data: CreateStaffRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": f"Staff account created with role {data.role}",
        "module": "staff",
        "labId": current_user.labId,
        "staff": {
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "role": data.role,
            "createdBy": current_user.userId,
        },
    }
