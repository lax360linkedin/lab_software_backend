# Medical Laboratory Management Software - Backend API

This backend provides a secure, multi-tenant FastAPI service for the Medical Laboratory Management System, featuring JWT authentication, Bcrypt password hashing, MongoDB Atlas persistence, strict multi-tenant data isolation, and comprehensive Role-Based Access Control (RBAC) across all 17 laboratory operational modules.

---

## 1. Python Environment

- **Recommended**: Python `3.10` or higher (tested on Python `3.14`)
- **Framework**: FastAPI with Pydantic v2 and Starlette
- **Database**: MongoDB Atlas / PyMongo

---

## 2. Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py             # Application settings & environment variables
│   │   ├── database.py           # MongoDB Atlas connection & unique indexes
│   │   ├── roles.py              # UserRole enum (admin, receptionist, lab_technician)
│   │   └── security.py           # Bcrypt hashing & PyJWT token handling
│   ├── dependencies/
│   │   ├── auth.py               # get_current_user JWT authentication dependency
│   │   └── rbac.py               # require_role, require_roles, ensure_lab_access
│   ├── models/
│   │   └── __init__.py           # LabDocument, UserDocument schema models
│   ├── routes/
│   │   ├── __init__.py           # Unified router exports
│   │   ├── auth.py               # /api/auth/signup, /login, /me
│   │   ├── rbac.py               # /api/rbac diagnostic & tenant isolation test routes
│   │   ├── dashboard.py          # /api/dashboard/summary, /activity
│   │   ├── patients.py           # /api/patients (registration & lookups)
│   │   ├── tests.py              # /api/tests (catalog, categories, test creation)
│   │   ├── samples.py            # /api/samples (accession, receiving, accept/reject)
│   │   ├── analysis.py           # /api/analysis (pending queue, processing, completed)
│   │   ├── results.py            # /api/results (entry, verification)
│   │   ├── reports.py            # /api/reports (listing, print preview, generation)
│   │   ├── billing.py            # /api/billing (invoices, receipts, payments)
│   │   ├── financial_analysis.py # /api/financial-analysis (revenue, collection stats)
│   │   ├── expenses.py           # /api/expenses (operational expenditures)
│   │   ├── doctors.py            # /api/doctors (referral doctor management)
│   │   ├── staff.py              # /api/staff (staff accounts & management)
│   │   ├── quality_control.py    # /api/quality-control (QC runs, calibration)
│   │   ├── lab_management.py     # /api/lab-management (departments, workflows)
│   │   ├── lab_profile.py        # /api/lab-profile (laboratory profile & branding)
│   │   ├── notifications.py      # /api/notifications (system alerts, broadcasts)
│   │   └── settings.py           # /api/settings (lab-level system configurations)
│   ├── schemas/
│   │   └── auth.py               # Pydantic request and response schemas
│   ├── services/
│   │   └── auth_service.py       # Authentication business logic & validations
│   └── main.py                   # FastAPI application initialization & route mounting
├── scripts/
│   ├── seed_test_users.py        # Idempotent development test user seeder
│   └── test_rbac_matrix.py       # Automated 178-test RBAC validation test suite
├── .env.example                  # Environment variables template
├── requirements.txt              # Production Python package requirements
└── README.md                     # Comprehensive backend documentation
```

---

## 3. Virtual Environment Setup

From the `backend/` directory:

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

---

## 5. MongoDB Setup

1. Create a free database on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) or run MongoDB locally on `mongodb://localhost:27017`.
2. Configure IP Access List in Atlas (`0.0.0.0/0` for development).
3. Set your connection string in `backend/.env` under `MONGODB_URI`.

### Unique Database Indexes
The backend automatically guarantees uniqueness across:
- `users.email` (unique)
- `users.userId` (unique)
- `labs.labId` (unique)

---

## 6. Environment Variables

Create a `.env` file in `backend/`:

```bash
cp .env.example .env
```

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `MONGODB_URI` | MongoDB Atlas or local connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Target database name | `lab_management` |
| `JWT_SECRET` | Secret key for signing JWT tokens (min 32 chars) | Secure random 32+ character secret |
| `JWT_ALGORITHM` | JWT hashing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | `60` |
| `FRONTEND_URL` | Allowed origin for CORS | `http://localhost:5173` |

---

## 7. Starting the Backend Server

From the `backend/` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

FastAPI server runs at `http://localhost:8000`.

### Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 8. Role-Based Access Control (RBAC) Architecture

### Roles
The system strictly enforces three distinct roles (`UserRole` enum):
1. **`admin`**: Primary laboratory administrator. Possesses full permissions across all 17 laboratory modules.
2. **`receptionist`**: Front-desk operations: patient registration/search, referral doctors, test selection, billing/invoicing, and viewing/printing permitted diagnostic reports.
3. **`lab_technician`**: Clinical operations: sample accession, receiving, acceptance/rejection, test analysis execution, parameter result entry, and quality control (QC) checks.

### Enforcement Rules
- **Authentication Check**: If no token or an invalid token is provided, returns `HTTP 401 Unauthorized`.
- **Role Permission Check**: If the authenticated user's role is not in the endpoint's permitted roles list, returns `HTTP 403 Forbidden` (`{"detail": "Insufficient permissions to access this resource."}`).
- **Multi-Tenant Isolation**: The user's `labId` is derived exclusively from the verified JWT identity (`current_user.labId`). Users can never access or query data outside their own laboratory tenant.

---

## 9. Comprehensive RBAC Permissions Matrix

| # | Module | Route Prefix | Operations | Admin | Receptionist | Lab Technician |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | **Dashboard** | `/api/dashboard` | View metrics & live activities | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| 2 | **Patients** | `/api/patients` | Register patients, view details & records | ✅ Allowed | ✅ Allowed | ❌ 403 Forbidden |
| 3 | **Tests Catalog** | `/api/tests` | View tests catalog & categories | ✅ Allowed | ✅ Allowed | ❌ 403 Forbidden |
| - | **Tests Management** | `POST /api/tests` | Create new diagnostic test definitions | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 4 | **Samples** | `/api/samples` | Accession, receive, accept/reject specimens | ✅ Allowed | ❌ 403 Forbidden | ✅ Allowed |
| 5 | **Analysis** | `/api/analysis` | Pending queue, process runs, completed runs | ✅ Allowed | ❌ 403 Forbidden | ✅ Allowed |
| 6 | **Results** | `/api/results` | Enter results, update values, verify results | ✅ Allowed | ❌ 403 Forbidden | ✅ Allowed |
| 7 | **Reports** | `/api/reports` | View report lists, print-view, generate report | ✅ Allowed | ✅ Allowed | ❌ 403 Forbidden |
| 8 | **Billing** | `/api/billing` | Create invoices, view billing & payment status | ✅ Allowed | ✅ Allowed | ❌ 403 Forbidden |
| 9 | **Financial Analysis** | `/api/financial-analysis` | Laboratory revenue, collection summaries | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 10 | **Expenses** | `/api/expenses` | Record & track operational expenses | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 11 | **Doctors** | `/api/doctors` | Referral doctor directory & onboarding | ✅ Allowed | ✅ Allowed | ❌ 403 Forbidden |
| 12 | **Staff** | `/api/staff` | Create & manage staff accounts | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 13 | **Quality Control** | `/api/quality-control` | QC check rules, submit control run results | ✅ Allowed | ❌ 403 Forbidden | ✅ Allowed |
| 14 | **Lab Management** | `/api/lab-management` | Department structure & workflow rules | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 15 | **Lab Profile** | `/api/lab-profile` | Laboratory name, address, contact, branding | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 16 | **Notifications** | `/api/notifications` | View system notices, broadcast alerts | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |
| 17 | **Settings** | `/api/settings` | Laboratory system configuration | ✅ Allowed | ❌ 403 Forbidden | ❌ 403 Forbidden |

---

## 10. Automated RBAC Matrix Test Suite

The project includes an automated test runner that validates all 178 role-permission-tenant combinations directly against the FastAPI application.

### Running the Test Suite
From the `backend/` directory:

```bash
python scripts/test_rbac_matrix.py
```

### What It Verifies:
1. Authenticates all 3 test users (`admin`, `receptionist`, `lab_technician`) and extracts valid JWT tokens.
2. Unauthenticated requests to protected endpoints return `401 Unauthorized`.
3. Tampered or invalid JWT signatures return `401 Unauthorized`.
4. Role permission enforcement:
   - Receptionist attempting clinical routes (`/api/samples`, `/api/analysis`, `/api/results`, `/api/quality-control`) $\rightarrow$ `403 Forbidden`.
   - Lab Technician attempting financial & front-desk routes (`/api/patients`, `/api/billing`, `/api/reports`, `/api/doctors`) $\rightarrow$ `403 Forbidden`.
   - Non-admins attempting administrative routes (`/api/expenses`, `/api/staff`, `/api/financial-analysis`, `/api/settings`, `/api/lab-management`, `/api/lab-profile`, `/api/notifications`) $\rightarrow$ `403 Forbidden`.
5. Multi-tenant isolation: Requests attempting to cross into another laboratory tenant (`resourceLabId != current_user.labId`) return `403 Forbidden`.

---

## 11. Testing with Postman

### Step 1: Seed Test Users
To generate development test users for all 3 roles, run:

```bash
python scripts/seed_test_users.py
```

### Pre-Seeded Test Credentials

| Role | Email | Password | Allowed Capabilities |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin@testlab.com` | `AdminPassword123!` | Full access to all 17 modules |
| **`receptionist`** | `receptionist@testlab.com` | `ReceptionistPass123!` | Patients, Tests Catalog, Billing, Reports, Doctors, Dashboard |
| **`lab_technician`** | `technician@testlab.com` | `TechnicianPass123!` | Samples, Analysis, Results, Quality Control, Dashboard |

---

### Step 2: Postman Request Walkthrough

#### 1. Login as Admin
- **POST** `http://localhost:8000/api/auth/login`
- **Body** (raw JSON):
  ```json
  {
    "email": "admin@testlab.com",
    "password": "AdminPassword123!"
  }
  ```
- **Response**: Copy the `accessToken`.

#### 2. Test Admin Capabilities
Set Header: `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`

- **GET** `http://localhost:8000/api/expenses` $\rightarrow$ `200 OK`
- **GET** `http://localhost:8000/api/financial-analysis/revenue` $\rightarrow$ `200 OK`
- **GET** `http://localhost:8000/api/staff` $\rightarrow$ `200 OK`
- **GET** `http://localhost:8000/api/patients` $\rightarrow$ `200 OK`
- **GET** `http://localhost:8000/api/samples` $\rightarrow$ `200 OK`

---

#### 3. Login as Receptionist
- **POST** `http://localhost:8000/api/auth/login`
- **Body** (raw JSON):
  ```json
  {
    "email": "receptionist@testlab.com",
    "password": "ReceptionistPass123!"
  }
  ```
- **Response**: Copy the `accessToken`.

#### 4. Test Receptionist Permissions
Set Header: `Authorization: Bearer <RECEPTIONIST_ACCESS_TOKEN>`

- **Allowed Requests**:
  - **GET** `http://localhost:8000/api/patients` $\rightarrow$ `200 OK`
  - **POST** `http://localhost:8000/api/patients` $\rightarrow$ `201 Created`
  - **GET** `http://localhost:8000/api/billing` $\rightarrow$ `200 OK`
  - **GET** `http://localhost:8000/api/reports` $\rightarrow$ `200 OK`
  - **GET** `http://localhost:8000/api/doctors` $\rightarrow$ `200 OK`
- **Forbidden Requests (`403 Forbidden`)**:
  - **GET** `http://localhost:8000/api/samples` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/analysis/pending` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/results` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/expenses` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/staff` $\rightarrow$ `403 Forbidden`

---

#### 5. Login as Lab Technician
- **POST** `http://localhost:8000/api/auth/login`
- **Body** (raw JSON):
  ```json
  {
    "email": "technician@testlab.com",
    "password": "TechnicianPass123!"
  }
  ```
- **Response**: Copy the `accessToken`.

#### 6. Test Lab Technician Permissions
Set Header: `Authorization: Bearer <TECHNICIAN_ACCESS_TOKEN>`

- **Allowed Requests**:
  - **GET** `http://localhost:8000/api/samples` $\rightarrow$ `200 OK`
  - **POST** `http://localhost:8000/api/samples/receive` $\rightarrow$ `200 OK`
  - **GET** `http://localhost:8000/api/analysis/pending` $\rightarrow$ `200 OK`
  - **POST** `http://localhost:8000/api/results/entry` $\rightarrow$ `201 Created`
  - **GET** `http://localhost:8000/api/quality-control/checks` $\rightarrow$ `200 OK`
- **Forbidden Requests (`403 Forbidden`)**:
  - **GET** `http://localhost:8000/api/patients` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/billing` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/reports` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/doctors` $\rightarrow$ `403 Forbidden`
  - **GET** `http://localhost:8000/api/expenses` $\rightarrow$ `403 Forbidden`

---

#### 7. Test Multi-Tenant Boundary
Set Header: `Authorization: Bearer <ANY_ROLE_ACCESS_TOKEN>`

- **GET** `http://localhost:8000/api/rbac/lab-isolation-test?resourceLabId=LAB-07947290` (matching user's labId) $\rightarrow$ `200 OK`
- **GET** `http://localhost:8000/api/rbac/lab-isolation-test?resourceLabId=LAB-OTHER-FORBIDDEN` $\rightarrow$ `403 Forbidden`
  ```json
  {
    "detail": "Cross-tenant access forbidden. Resource does not belong to your laboratory."
  }
  ```

---

#### 8. Test Unauthenticated Requests
Send any request without `Authorization` header:

- **GET** `http://localhost:8000/api/patients` $\rightarrow$ `401 Unauthorized`
  ```json
  {
    "detail": "Not authenticated"
  }
  ```
