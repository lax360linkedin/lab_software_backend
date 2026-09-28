from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


class PatientRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Patient full name")
    phone: str = Field(..., min_length=5, description="Patient contact number")
    gender: Optional[str] = Field("other", description="Patient gender")
    age: Optional[int] = Field(None, ge=0, description="Patient age")


@router.get(
    "",
    summary="Search and list patients",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def list_patients(
    query: Optional[str] = Query(None, description="Search term for patient name or phone"),
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "patients",
        "labId": current_user.labId,
        "query": query,
        "total": 0,
        "patients": [],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def register_patient(
    data: PatientRegistrationRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "message": "Patient registered successfully",
        "module": "patients",
        "labId": current_user.labId,
        "patient": {
            "name": data.name,
            "phone": data.phone,
            "gender": data.gender,
            "age": data.age,
            "registeredBy": current_user.userId,
        },
    }


@router.get(
    "/{patient_id}",
    summary="Get patient details",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def get_patient_details(
    patient_id: str,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "patients",
        "labId": current_user.labId,
        "patientId": patient_id,
        "details": None,
    }
