from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


class GenerateReportRequest(BaseModel):
    patientId: str = Field(..., description="ID of patient")
    resultIds: list[str] = Field(..., description="List of verified result IDs to compile")


@router.get(
    "",
    summary="List permitted diagnostic reports",
    description="Accessible by Admin and Receptionist for viewing. Unauthorized for Lab Technician (403).",
)
def list_reports(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "reports",
        "labId": current_user.labId,
        "total": 0,
        "reports": [],
    }


@router.get(
    "/{report_id}/print",
    summary="View and print permitted report",
    description="Accessible by Admin and Receptionist for report viewing/printing. Unauthorized for Lab Technician (403).",
)
def print_report(
    report_id: str,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "reports",
        "labId": current_user.labId,
        "reportId": report_id,
        "printableFormat": "ready",
        "requestedBy": current_user.userId,
    }


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate diagnostic report",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def generate_report(
    data: GenerateReportRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "message": "Report generated successfully",
        "module": "reports",
        "labId": current_user.labId,
        "patientId": data.patientId,
        "generatedBy": current_user.userId,
    }
