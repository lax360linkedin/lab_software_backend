from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/doctors", tags=["Doctors"])


class DoctorCreateRequest(BaseModel):
    name: str = Field(..., description="Doctor full name")
    specialty: Optional[str] = Field("General Medicine", description="Medical specialty")
    phone: Optional[str] = Field(None, description="Doctor contact number")
    clinicOrHospital: Optional[str] = Field(None, description="Hospital or clinic affiliation")


@router.get(
    "",
    summary="List referral doctors and details",
    description="Accessible by Admin and Receptionist for referral management. Unauthorized for Lab Technician (403).",
)
def list_doctors(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "doctors",
        "labId": current_user.labId,
        "total": 0,
        "doctors": [],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Register a referral doctor",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def create_doctor(
    data: DoctorCreateRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "message": "Doctor registered successfully",
        "module": "doctors",
        "labId": current_user.labId,
        "doctor": {
            "name": data.name,
            "specialty": data.specialty,
            "phone": data.phone,
            "clinicOrHospital": data.clinicOrHospital,
            "registeredBy": current_user.userId,
        },
    }
