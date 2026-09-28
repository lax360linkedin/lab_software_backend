from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class ProcessAnalysisRequest(BaseModel):
    sampleId: str = Field(..., description="ID of sample under analysis")
    testId: str = Field(..., description="ID of test to be performed")


@router.get(
    "/pending",
    summary="Get pending tests for analysis",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def get_pending_analysis(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "analysis",
        "labId": current_user.labId,
        "totalPending": 0,
        "queue": [],
    }


@router.post(
    "/process",
    status_code=status.HTTP_200_OK,
    summary="Process laboratory test analysis",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def process_analysis(
    data: ProcessAnalysisRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Analysis started/processing",
        "module": "analysis",
        "labId": current_user.labId,
        "sampleId": data.sampleId,
        "testId": data.testId,
        "operator": current_user.userId,
    }


@router.get(
    "/completed",
    summary="Get completed analyses",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def get_completed_analysis(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "analysis",
        "labId": current_user.labId,
        "completed": [],
    }
