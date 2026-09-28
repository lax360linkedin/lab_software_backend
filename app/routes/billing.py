from typing import List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/billing", tags=["Billing"])


class CreateInvoiceRequest(BaseModel):
    patientId: str = Field(..., description="ID of patient")
    testIds: List[str] = Field(..., description="List of tests billed")
    amountPaid: float = Field(0.0, ge=0, description="Amount received upfront")
    paymentMethod: str = Field("cash", description="Payment method: cash, card, online")


@router.get(
    "",
    summary="List bills and payment status",
    description="Accessible by Admin and Receptionist for billing and payment tracking. Unauthorized for Lab Technician (403).",
)
def list_billing(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "billing",
        "labId": current_user.labId,
        "total": 0,
        "invoices": [],
    }


@router.post(
    "/invoice",
    status_code=status.HTTP_201_CREATED,
    summary="Create new bill and record payment",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def create_invoice(
    data: CreateInvoiceRequest,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "message": "Bill generated successfully",
        "module": "billing",
        "labId": current_user.labId,
        "invoice": {
            "patientId": data.patientId,
            "testCount": len(data.testIds),
            "amountPaid": data.amountPaid,
            "paymentMethod": data.paymentMethod,
            "billedBy": current_user.userId,
        },
    }


@router.get(
    "/{bill_id}",
    summary="Get invoice payment details",
    description="Accessible by Admin and Receptionist. Unauthorized for Lab Technician (403).",
)
def get_invoice_details(
    bill_id: str,
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "billing",
        "labId": current_user.labId,
        "billId": bill_id,
        "details": None,
    }
