"""
Authentication & RBAC Strict Verification Test Suite
===================================================
Tests all 10 specific acceptance scenarios requested by the user:
1. Correct Admin credentials -> 200 + JWT + role=admin
2. Wrong Admin password -> 401
3. Non-existing Admin email -> 401
4. Correct Receptionist credentials -> 200 + role=receptionist
5. Wrong Receptionist password -> 401
6. Correct Lab Technician credentials -> 200 + role=lab_technician
7. Wrong Lab Technician password -> 401
8. Receptionist calling Admin-only API -> 403
9. Lab Technician calling Admin-only API -> 403
10. No JWT calling protected API -> 401
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

results = []


def run_test(name: str, passed: bool, details: str):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, details))
    print(f"[{status}] {name}: {details}")


def main():
    print("=" * 80)
    print("RUNNING STRICT AUTHENTICATION & RBAC SCENARIO VERIFICATION")
    print("=" * 80)

    # 1. Correct Admin credentials -> 200, JWT, role=admin
    r = client.post("/api/auth/login", json={"email": "admin@testlab.com", "password": "AdminPassword123!"})
    d = r.json() if r.status_code == 200 else {}
    passed = r.status_code == 200 and "accessToken" in d and d.get("user", {}).get("role") == "admin"
    admin_token = d.get("accessToken", "")
    run_test("1. Correct Admin credentials", passed, f"Status: {r.status_code}, Role: {d.get('user', {}).get('role')}")

    # 2. Wrong Admin password -> 401
    r = client.post("/api/auth/login", json={"email": "admin@testlab.com", "password": "WrongPasswordXYZ!"})
    passed = r.status_code == 401
    run_test("2. Wrong Admin password", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # 3. Non-existing Admin email -> 401
    r = client.post("/api/auth/login", json={"email": "nonexistent_admin@testlab.com", "password": "AdminPassword123!"})
    passed = r.status_code == 401
    run_test("3. Non-existing Admin email", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # 4. Correct Receptionist credentials -> 200, role=receptionist
    r = client.post("/api/auth/login", json={"email": "receptionist@testlab.com", "password": "ReceptionistPass123!"})
    d = r.json() if r.status_code == 200 else {}
    passed = r.status_code == 200 and "accessToken" in d and d.get("user", {}).get("role") == "receptionist"
    receptionist_token = d.get("accessToken", "")
    run_test("4. Correct Receptionist credentials", passed, f"Status: {r.status_code}, Role: {d.get('user', {}).get('role')}")

    # 5. Wrong Receptionist password -> 401
    r = client.post("/api/auth/login", json={"email": "receptionist@testlab.com", "password": "InvalidPassword123!"})
    passed = r.status_code == 401
    run_test("5. Wrong Receptionist password", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # 6. Correct Lab Technician credentials -> 200, role=lab_technician
    r = client.post("/api/auth/login", json={"email": "technician@testlab.com", "password": "TechnicianPass123!"})
    d = r.json() if r.status_code == 200 else {}
    passed = r.status_code == 200 and "accessToken" in d and d.get("user", {}).get("role") == "lab_technician"
    tech_token = d.get("accessToken", "")
    run_test("6. Correct Lab Technician credentials", passed, f"Status: {r.status_code}, Role: {d.get('user', {}).get('role')}")

    # 7. Wrong Lab Technician password -> 401
    r = client.post("/api/auth/login", json={"email": "technician@testlab.com", "password": "BadPassword123!"})
    passed = r.status_code == 401
    run_test("7. Wrong Lab Technician password", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # 8. Receptionist calling Admin-only API -> 403
    r = client.get("/api/expenses", headers={"Authorization": f"Bearer {receptionist_token}"})
    passed = r.status_code == 403
    run_test("8. Receptionist calling Admin-only API (/api/expenses)", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # 9. Lab Technician calling Admin-only API -> 403
    r = client.get("/api/expenses", headers={"Authorization": f"Bearer {tech_token}"})
    passed = r.status_code == 403
    run_test("9. Lab Technician calling Admin-only API (/api/expenses)", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # 10. No JWT calling protected API -> 401
    r = client.get("/api/expenses")
    passed = r.status_code == 401
    run_test("10. No JWT calling protected API (/api/expenses)", passed, f"Status: {r.status_code}, Detail: {r.json().get('detail')}")

    # Extra: Also verify reception@abc.com returns role=receptionist
    r = client.post("/api/auth/login", json={"email": "reception@abc.com", "password": "AdminPassword123!"})
    if r.status_code == 401:
        # Might have another password, test just finding role
        pass
    else:
        d = r.json()
        print(f"[INFO] reception@abc.com role returned from backend: {d.get('user', {}).get('role')}")

    print("=" * 80)
    all_passed = all(status == "PASS" for _, status, _ in results)
    if all_passed:
        print("ALL 10 TARGET CRITERIA PASSED WITHOUT EXCEPTION!")
    else:
        print("SOME TESTS FAILED! CHECK OUTPUT ABOVE.")
        sys.exit(1)


if __name__ == "__main__":
    main()
