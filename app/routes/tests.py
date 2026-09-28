from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_role, require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/tests", tags=["Tests"])


class TestCreateRequest(BaseModel):
    testName: str = Field(..., min_length=1, description="Laboratory test name")
    category: str = Field(..., min_length=1, description="Test category")
    price: float = Field(..., ge=0, description="Test pricing")


@router.get(
    "",
    summary="List and select laboratory tests",
    description="Accessible by Admin and Receptionist for test selection. Unauthorized for Lab Technician (403).",
)
def list_tests(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "tests",
        "labId": current_user.labId,
        "total": 0,
        "tests": [],
    }


@router.get(
    "/categories",
    summary="List test categories",
    description="Accessible by Admin and Receptionist.",
)
def list_test_categories(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "module": "tests",
        "labId": current_user.labId,
        "categories": ["Biochemistry", "Hematology", "Microbiology", "Immunology", "Pathology"],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new laboratory test (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def create_test(
    data: TestCreateRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Laboratory test created successfully",
        "module": "tests",
        "labId": current_user.labId,
        "test": {
            "testName": data.testName,
            "category": data.category,
            "price": data.price,
            "createdBy": current_user.userId,
        },
    }
