"""
RBAC Matrix Test Suite
=======================
Automated test suite verifying complete role-based access control enforcement
across all 17 laboratory modules, authentication endpoints, and tenant isolation.

Executes direct HTTP requests against the FastAPI app via TestClient.
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

USERS = {
    "admin": {
        "email": "admin@testlab.com",
        "password": "AdminPassword123!",
    },
    "receptionist": {
        "email": "receptionist@testlab.com",
        "password": "ReceptionistPass123!",
    },
    "lab_technician": {
        "email": "technician@testlab.com",
        "password": "TechnicianPass123!",
    },
}

tokens = {}
lab_ids = {}
results = {"passed": 0, "failed": 0, "total": 0}


def log_test(module: str, method: str, endpoint: str, role: str, expected: int, actual: int):
    results["total"] += 1
    passed = actual == expected
    if passed:
        results["passed"] += 1
        status = "[PASS]"
    else:
        results["failed"] += 1
        status = "[FAIL]"
    print(f"{status} | {module:<20} | {method:<6} {endpoint:<38} | Role: {role:<15} | Expected: {expected} | Actual: {actual}")


def login_users():
    print("\n" + "=" * 90)
    print("STEP 1: AUTHENTICATING TEST USERS & RETRIEVING JWT TOKENS")
    print("=" * 90)
    for role, creds in USERS.items():
        resp = client.post("/api/auth/login", json=creds)
        assert resp.status_code == 200, f"Login failed for {role}: {resp.text}"
        data = resp.json()
        tokens[role] = data["accessToken"]
        user_info = data["user"]
        lab_ids[role] = user_info["labId"]
        print(f"Logged in as {role.upper():<14} | User ID: {user_info['userId']} | Lab ID: {user_info['labId']} | Token received")
    print("All 3 roles authenticated successfully.\n")


def test_auth_and_me():
    print("=" * 90)
    print("STEP 2: TESTING /api/auth/me AND UNPROTECTED / HEALTH ENDPOINTS")
    print("=" * 90)
    # Health checks
    r = client.get("/api/health")
    log_test("Health Check", "GET", "/api/health", "anonymous", 200, r.status_code)
    
    r = client.get("/")
    log_test("Root Health", "GET", "/", "anonymous", 200, r.status_code)

    # /api/auth/me unauthenticated -> 401
    r = client.get("/api/auth/me")
    log_test("Auth Me", "GET", "/api/auth/me", "anonymous", 401, r.status_code)

    # /api/auth/me invalid token -> 401
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
    log_test("Auth Me", "GET", "/api/auth/me", "invalid_jwt", 401, r.status_code)

    # /api/auth/me authenticated
    for role in ["admin", "receptionist", "lab_technician"]:
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        r = client.get("/api/auth/me", headers=headers)
        log_test("Auth Me", "GET", "/api/auth/me", role, 200, r.status_code)


def test_rbac_verification_routes():
    print("\n" + "=" * 90)
    print("STEP 3: TESTING RBAC DIAGNOSTIC TEST ENDPOINTS (/api/rbac/*)")
    print("=" * 90)
    endpoints = [
        ("/api/rbac/admin-test", {"admin": 200, "receptionist": 403, "lab_technician": 403}),
        ("/api/rbac/receptionist-test", {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("/api/rbac/lab-technician-test", {"admin": 200, "receptionist": 403, "lab_technician": 200}),
    ]

    for ep, matrix in endpoints:
        # Test anonymous -> 401
        r = client.get(ep)
        log_test("RBAC Diagnostic", "GET", ep, "anonymous", 401, r.status_code)
        
        for role, exp in matrix.items():
            headers = {"Authorization": f"Bearer {tokens[role]}"}
            r = client.get(ep, headers=headers)
            log_test("RBAC Diagnostic", "GET", ep, role, exp, r.status_code)

    # Multi-tenant isolation verification test
    iso_ep = "/api/rbac/lab-isolation-test"
    # Anonymous -> 401
    r = client.get(iso_ep, params={"resourceLabId": "ANY"})
    log_test("Tenant Isolation", "GET", iso_ep, "anonymous", 401, r.status_code)

    for role in ["admin", "receptionist", "lab_technician"]:
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        # Matching tenant -> 200
        r = client.get(iso_ep, params={"resourceLabId": lab_ids[role]}, headers=headers)
        log_test("Tenant Isolation Valid", "GET", iso_ep, role, 200, r.status_code)

        # Cross-tenant attempt -> 403 Forbidden
        r = client.get(iso_ep, params={"resourceLabId": "LAB-CROSS-TENANT-FORBIDDEN"}, headers=headers)
        log_test("Tenant Isolation Cross", "GET", iso_ep, role, 403, r.status_code)


def test_laboratory_modules():
    print("\n" + "=" * 90)
    print("STEP 4: TESTING ALL 17 LABORATORY MODULES ACROSS ALL 3 ROLES")
    print("=" * 90)

    # Test cases: (module, method, endpoint, payload, expected_status_per_role)
    test_cases = [
        # 1. Dashboard (Admin, Receptionist, Technician)
        ("Dashboard Summary", "GET", "/api/dashboard/summary", None, {"admin": 200, "receptionist": 200, "lab_technician": 200}),
        ("Dashboard Activity", "GET", "/api/dashboard/activity", None, {"admin": 200, "receptionist": 200, "lab_technician": 200}),

        # 2. Patients (Admin, Receptionist only - Technician forbidden)
        ("Patients List", "GET", "/api/patients", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Patient Details", "GET", "/api/patients/PAT-001", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Patient Create", "POST", "/api/patients", {
            "name": "Jane Doe",
            "age": 28,
            "gender": "Female",
            "phone": "9876500000"
        }, {"admin": 201, "receptionist": 201, "lab_technician": 403}),

        # 3. Tests (Read: Admin, Receptionist; Create: Admin only)
        ("Tests Catalog", "GET", "/api/tests", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Test Categories", "GET", "/api/tests/categories", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Test Create", "POST", "/api/tests", {
            "testName": "Complete Blood Count",
            "category": "Hematology",
            "price": 450.0
        }, {"admin": 201, "receptionist": 403, "lab_technician": 403}),

        # 4. Samples (Admin, Technician only - Receptionist forbidden)
        ("Samples List", "GET", "/api/samples", None, {"admin": 200, "receptionist": 403, "lab_technician": 200}),
        ("Sample Accession", "POST", "/api/samples/accession", {
            "patientId": "PAT-001",
            "sampleType": "EDTA Blood"
        }, {"admin": 201, "receptionist": 403, "lab_technician": 201}),
        ("Sample Receive", "POST", "/api/samples/receive", {
            "barcode": "SMP-2026-0001"
        }, {"admin": 200, "receptionist": 403, "lab_technician": 200}),

        # 5. Analysis (Admin, Technician only - Receptionist forbidden)
        ("Analysis Pending", "GET", "/api/analysis/pending", None, {"admin": 200, "receptionist": 403, "lab_technician": 200}),
        ("Analysis Completed", "GET", "/api/analysis/completed", None, {"admin": 200, "receptionist": 403, "lab_technician": 200}),
        ("Analysis Process", "POST", "/api/analysis/process", {
            "sampleId": "SMP-001",
            "testId": "TST-CBC-001"
        }, {"admin": 200, "receptionist": 403, "lab_technician": 200}),

        # 6. Results (Admin, Technician only - Receptionist forbidden)
        ("Results List", "GET", "/api/results", None, {"admin": 200, "receptionist": 403, "lab_technician": 200}),
        ("Results Entry", "POST", "/api/results/entry", {
            "sampleId": "SMP-001",
            "testId": "TST-CBC-001",
            "parameterValues": {
                "Hemoglobin": "14.2 g/dL",
                "WBC": "7200 /mcL"
            }
        }, {"admin": 201, "receptionist": 403, "lab_technician": 201}),
        ("Results Verify", "POST", "/api/results/verify", {
            "resultId": "RES-001",
            "verified": True,
            "remarks": "Clinically normal"
        }, {"admin": 200, "receptionist": 403, "lab_technician": 200}),

        # 7. Reports (Admin, Receptionist - Technician forbidden)
        ("Reports List", "GET", "/api/reports", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Report Print View", "GET", "/api/reports/REP-001/print", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Report Generate", "POST", "/api/reports/generate", {
            "patientId": "PAT-001",
            "resultIds": ["RES-001"]
        }, {"admin": 201, "receptionist": 201, "lab_technician": 403}),

        # 8. Billing (Admin, Receptionist - Technician forbidden)
        ("Billing List", "GET", "/api/billing", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Billing Details", "GET", "/api/billing/INV-001", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Invoice Create", "POST", "/api/billing/invoice", {
            "patientId": "PAT-001",
            "testIds": ["TST-CBC-001"],
            "amountPaid": 450.0,
            "paymentMethod": "UPI"
        }, {"admin": 201, "receptionist": 201, "lab_technician": 403}),

        # 9. Financial Analysis (Admin only)
        ("Financial Revenue", "GET", "/api/financial-analysis/revenue", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),
        ("Financial Collections", "GET", "/api/financial-analysis/collection-summary", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),

        # 10. Expenses (Admin only)
        ("Expenses List", "GET", "/api/expenses", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),
        ("Expense Create", "POST", "/api/expenses", {
            "category": "Supplies",
            "amount": 12500.0,
            "description": "Monthly reagents purchase and buffer solution restock"
        }, {"admin": 201, "receptionist": 403, "lab_technician": 403}),

        # 11. Doctors / Referrals (Admin, Receptionist - Technician forbidden)
        ("Doctors List", "GET", "/api/doctors", None, {"admin": 200, "receptionist": 200, "lab_technician": 403}),
        ("Doctor Create", "POST", "/api/doctors", {
            "name": "Dr. Sarah Connor",
            "specialization": "Pathology",
            "phone": "9876543299",
            "clinic": "Metro Clinic"
        }, {"admin": 201, "receptionist": 201, "lab_technician": 403}),

        # 12. Staff Management (Admin only)
        ("Staff List", "GET", "/api/staff", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),
        ("Staff Create", "POST", "/api/staff", {
            "name": "Sam Assistant",
            "email": "sam@testlab.com",
            "role": "receptionist",
            "phone": "9876543288",
            "password": "TemporaryPass123!"
        }, {"admin": 201, "receptionist": 403, "lab_technician": 403}),

        # 13. Quality Control (Admin, Technician - Receptionist forbidden)
        ("QC Checks List", "GET", "/api/quality-control/checks", None, {"admin": 200, "receptionist": 403, "lab_technician": 200}),
        ("QC Result Submit", "POST", "/api/quality-control/results", {
            "controlId": "CTRL-CBC-NORMAL",
            "instrumentId": "INST-HEMATOLOGY-01",
            "measurements": {
                "parameter": "Hemoglobin",
                "measuredValue": 14.1,
                "targetValue": 14.0,
                "status": "PASS"
            }
        }, {"admin": 201, "receptionist": 403, "lab_technician": 201}),

        # 14. Lab Management (Admin only)
        ("Lab Departments", "GET", "/api/lab-management/departments", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),

        # 15. Lab Profile (Admin only)
        ("Lab Profile", "GET", "/api/lab-profile", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),

        # 16. Notifications (Admin only)
        ("Notifications List", "GET", "/api/notifications", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),
        ("Notification Broadcast", "POST", "/api/notifications/broadcast", {
            "recipientRole": "all",
            "message": "Routine server calibration tonight at 10 PM."
        }, {"admin": 201, "receptionist": 403, "lab_technician": 403}),

        # 17. Settings (Admin only)
        ("Settings View", "GET", "/api/settings", None, {"admin": 200, "receptionist": 403, "lab_technician": 403}),
    ]

    for module, method, endpoint, payload, expected_map in test_cases:
        # First verify unauthenticated gets 401
        if method == "GET":
            unauth_r = client.get(endpoint)
        elif method == "POST":
            unauth_r = client.post(endpoint, json=payload or {})
        log_test(module, method, endpoint, "unauthenticated", 401, unauth_r.status_code)

        # Verify each role
        for role, expected_code in expected_map.items():
            headers = {"Authorization": f"Bearer {tokens[role]}"}
            if method == "GET":
                resp = client.get(endpoint, headers=headers)
            elif method == "POST":
                resp = client.post(endpoint, json=payload or {}, headers=headers)
            log_test(module, method, endpoint, role, expected_code, resp.status_code)


def print_summary():
    print("\n" + "=" * 90)
    print("RBAC TEST SUITE EXECUTION SUMMARY")
    print("=" * 90)
    print(f"Total Tests Run : {results['total']}")
    print(f"Passed          : {results['passed']}")
    print(f"Failed          : {results['failed']}")
    print("=" * 90)
    if results["failed"] == 0:
        print("[SUCCESS] ALL ROLE-BASED ACCESS CONTROL TESTS PASSED PERFECTLY!\n")
    else:
        print(f"[ALERT] {results['failed']} TEST(S) FAILED! CHECK OUTPUT ABOVE.\n")
        sys.exit(1)


if __name__ == "__main__":
    login_users()
    test_auth_and_me()
    test_rbac_verification_routes()
    test_laboratory_modules()
    print_summary()
