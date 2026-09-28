from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/quality-control", tags=["Quality Control"])


class RecordQCResultRequest(BaseModel):
    controlId: str = Field(..., description="ID of control specimen")
    instrumentId: str = Field(..., description="Analyzer or equipment ID")
    measurements: Dict[str, Any] = Field(..., description="QC measurements and values")


@router.get(
    "/checks",
    summary="Get quality control checks and status",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def get_qc_checks(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "quality-control",
        "labId": current_user.labId,
        "qcStatus": "passed",
        "checks": [],
    }


@router.post(
    "/results",
    status_code=status.HTTP_201_CREATED,
    summary="Record QC run result",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def record_qc_result(
    data: RecordQCResultRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Quality control result recorded",
        "module": "quality-control",
        "labId": current_user.labId,
        "controlId": data.controlId,
        "recordedBy": current_user.userId,
    }
