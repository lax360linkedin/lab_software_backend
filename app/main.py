from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.routes import (
    auth_router,
    rbac_router,
    dashboard_router,
    patients_router,
    tests_router,
    samples_router,
    analysis_router,
    results_router,
    reports_router,
    billing_router,
    financial_analysis_router,
    expenses_router,
    doctors_router,
    staff_router,
    quality_control_router,
    lab_management_router,
    lab_profile_router,
    notifications_router,
    settings_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database connection and indexes
    init_db()
    yield
    # Shutdown: clean up database connections
    close_db()


app = FastAPI(
    title="Medical Laboratory Management API",
    description="Backend API for Laboratory Authentication and Management (Phase 1)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(auth_router, prefix="/api")
app.include_router(rbac_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(tests_router, prefix="/api")
app.include_router(samples_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(results_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(financial_analysis_router, prefix="/api")
app.include_router(expenses_router, prefix="/api")
app.include_router(doctors_router, prefix="/api")
app.include_router(staff_router, prefix="/api")
app.include_router(quality_control_router, prefix="/api")
app.include_router(lab_management_router, prefix="/api")
app.include_router(lab_profile_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "Medical Laboratory Management Backend API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
