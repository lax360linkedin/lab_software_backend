from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/samples", tags=["Samples"])


class SampleAccessionRequest(BaseModel):
    patientId: str = Field(..., description="ID of patient associated with sample")
    sampleType: str = Field(..., description="Type of biological specimen (e.g. Blood, Urine)")
    barcode: Optional[str] = Field(None, description="Optional pre-assigned barcode")


class SampleStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Sample status: accepted or rejected")
    rejectionReason: Optional[str] = Field(None, description="Reason if specimen rejected")


@router.get(
    "",
    summary="List laboratory samples",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def list_samples(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "samples",
        "labId": current_user.labId,
        "total": 0,
        "samples": [],
    }


@router.post(
    "/accession",
    status_code=status.HTTP_201_CREATED,
    summary="Accession new specimen",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def accession_sample(
    data: SampleAccessionRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Sample accessioned successfully",
        "module": "samples",
        "labId": current_user.labId,
        "sample": {
            "patientId": data.patientId,
            "sampleType": data.sampleType,
            "barcode": data.barcode or "BAR-DEMO",
            "accessionedBy": current_user.userId,
        },
    }


class ReceiveSampleRequest(BaseModel):
    barcode: str = Field(..., description="Sample barcode for identification")


@router.post(
    "/receive",
    summary="Receive and identify sample",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def receive_sample(
    data: ReceiveSampleRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Sample received and identified",
        "module": "samples",
        "labId": current_user.labId,
        "barcode": data.barcode,
        "receivedBy": current_user.userId,
    }



@router.patch(
    "/{sample_id}/status",
    summary="Accept or reject sample",
    description="Accessible by Admin and Lab Technician. Unauthorized for Receptionist (403).",
)
def update_sample_status(
    sample_id: str,
    data: SampleStatusUpdateRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": f"Sample status updated to {data.status}",
        "module": "samples",
        "labId": current_user.labId,
        "sampleId": sample_id,
        "status": data.status,
        "rejectionReason": data.rejectionReason,
        "evaluatedBy": current_user.userId,
    }
