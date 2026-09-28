from .auth import router as auth_router
from .rbac import router as rbac_router
from .dashboard import router as dashboard_router
from .patients import router as patients_router
from .tests import router as tests_router
from .samples import router as samples_router
from .analysis import router as analysis_router
from .results import router as results_router
from .reports import router as reports_router
from .billing import router as billing_router
from .financial_analysis import router as financial_analysis_router
from .expenses import router as expenses_router
from .doctors import router as doctors_router
from .staff import router as staff_router
from .quality_control import router as quality_control_router
from .lab_management import router as lab_management_router
from .lab_profile import router as lab_profile_router
from .notifications import router as notifications_router
from .settings import router as settings_router

__all__ = [
    "auth_router",
    "rbac_router",
    "dashboard_router",
    "patients_router",
    "tests_router",
    "samples_router",
    "analysis_router",
    "results_router",
    "reports_router",
    "billing_router",
    "financial_analysis_router",
    "expenses_router",
    "doctors_router",
    "staff_router",
    "quality_control_router",
    "lab_management_router",
    "lab_profile_router",
    "notifications_router",
    "settings_router",
]
