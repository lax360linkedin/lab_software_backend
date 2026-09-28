from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/results", tags=["Results"])


class ResultEntryRequest(BaseModel):
    sampleId: str = Field(..., description="ID of sample")
    testId: str = Field(..., description="ID of test")
    parameterValues: Dict[str, Any] = Field(..., description="Key-value test parameter measurements")
    notes: Optional[str] = Field(None, description="Technician observations")


class ResultVerifyRequest(BaseModel):
    resultId: str = Field(..., description="ID of test result to verify")
    verificationStatus: str = Field("verified", description="Status: verified or review_required")
    remarks: Optional[str] = Field(None, description="Verification remarks")


@router.get(
    "",
    summary="List laboratory test results",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def list_results(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "results",
        "labId": current_user.labId,
        "total": 0,
        "results": [],
    }


@router.post(
    "/entry",
    status_code=status.HTTP_201_CREATED,
    summary="Enter or update test results",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def enter_results(
    data: ResultEntryRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Results recorded successfully",
        "module": "results",
        "labId": current_user.labId,
        "entry": {
            "sampleId": data.sampleId,
            "testId": data.testId,
            "enteredBy": current_user.userId,
            "parameterValues": data.parameterValues,
        },
    }


@router.post(
    "/verify",
    summary="Authorize and verify test result",
    description="Accessible by Admin and Lab Technician (authorized verification). Unauthorized for Receptionist (403).",
)
def verify_result(
    data: ResultVerifyRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Result verified successfully",
        "module": "results",
        "labId": current_user.labId,
        "resultId": data.resultId,
        "verifiedBy": current_user.userId,
        "verificationStatus": data.verificationStatus,
    }
