# 🔥 Fire NOC Management System

A complete Full Stack Web Application for Fire Department offices to digitally manage fire safety inspections, follow-ups, and NOC issuance.

---

## 📋 Project Overview

| Item | Details |
|------|---------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Backend** | Python Flask |
| **Database** | MySQL |
| **Auth** | JWT (JSON Web Tokens) |
| **Tools** | VS Code, MySQL Workbench, Postman |

---

## 👥 User Roles

| Role | Default Credentials |
|------|-------------------|
| Admin | `admin` / `Admin@123` |
| Inspector | `inspector1` / `Admin@123` |
| Applicant | `applicant1` / `Admin@123` |

---

## 📁 Project Structure

```
fire_noc_system/
├── frontend/
│   ├── css/
│   │   ├── style.css          # Main stylesheet
│   │   └── auth.css           # Login/Register styles
│   ├── js/
│   │   ├── main.js            # API utilities, helpers
│   │   └── layout.js          # Sidebar/navbar builder
│   ├── pages/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── admin-dashboard.html
│   │   ├── inspector-dashboard.html
│   │   ├── applicant-dashboard.html
│   │   ├── application-form.html
│   │   ├── inspection-management.html
│   │   ├── followup-management.html
│   │   ├── noc-management.html
│   │   ├── application-status.html
│   │   ├── notifications.html
│   │   ├── reports.html
│   │   ├── profile.html
│   │   └── error.html
│   └── index.html             # Landing page
│
├── backend/
│   ├── app.py                 # Main Flask app
│   ├── config.py              # Configuration
│   ├── extensions.py          # Flask extensions
│   ├── requirements.txt       # Python packages
│   ├── database.sql           # MySQL schema + seed data
│   ├── models/
│   │   └── models.py          # SQLAlchemy models
│   ├── routes/
│   │   ├── auth_routes.py     # Login, register, profile
│   │   ├── application_routes.py
│   │   └── other_routes.py    # Inspections, NOC, etc.
│   └── uploads/
│       ├── documents/
│       ├── inspections/
│       └── noc/
│
├── README.md
└── setup_guide.txt
```

---

## ⚙️ Installation Steps

### Step 1 — Prerequisites
- Python 3.10+
- MySQL Server + MySQL Workbench
- VS Code

### Step 2 — Clone / Extract the Project
```bash
cd C:\Projects
# Extract fire_noc_system.zip here
```

### Step 3 — Set Up MySQL Database
1. Open **MySQL Workbench**
2. Connect to `localhost` with your root credentials
3. Go to **File → Open SQL Script**
4. Open `backend/database.sql`
5. Click ▶ **Execute All**
6. Refresh the schema list — you should see `fire_noc_db`

### Step 4 — Configure Database Password
Open `backend/config.py` and set your MySQL password:
```python
DB_PASSWORD = 'your_mysql_password'   # ← change this
```

### Step 5 — Create Python Virtual Environment
```bash
cd fire_noc_system/backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 6 — Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 7 — Run the Flask Server
```bash
python app.py
```
You should see:
```
✅  Database tables verified / created.
🔥  Fire NOC System running at http://localhost:5000
```

### Step 8 — Open the Application
Open your browser and go to:
```
http://localhost:5000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login |
| GET | `/api/profile` | Get own profile |
| PUT | `/api/profile` | Update profile |
| GET | `/api/users` | All users (admin) |
| POST | `/api/applications` | Submit application |
| GET | `/api/applications` | List applications |
| GET | `/api/applications/<id>` | Single application |
| PUT | `/api/applications/<id>` | Update application |
| DELETE | `/api/applications/<id>` | Delete (admin) |
| POST | `/api/inspections` | Create inspection |
| GET | `/api/inspections` | List inspections |
| PUT | `/api/inspections/<id>` | Update inspection |
| POST | `/api/inspections/upload-image/<id>` | Upload photo |
| POST | `/api/followups` | Create follow-up |
| GET | `/api/followups` | List follow-ups |
| PUT | `/api/followups/<id>` | Update follow-up |
| POST | `/api/noc/approve` | Approve NOC |
| POST | `/api/noc/reject` | Reject NOC |
| GET | `/api/noc/<application_id>` | Get NOC |
| GET | `/api/noc` | All NOC records |
| POST | `/api/upload-document` | Upload document |
| GET | `/api/documents/<app_id>` | Get documents |
| GET | `/api/notifications/<user_id>` | Get notifications |
| PUT | `/api/notifications/mark-read/<id>` | Mark read |
| GET | `/api/dashboard/admin` | Admin dashboard data |
| GET | `/api/dashboard/inspector` | Inspector dashboard |
| GET | `/api/dashboard/applicant` | Applicant dashboard |
| GET | `/api/health` | Health check |

---

## 🧪 Testing with Postman

### Login (get token):
```
POST http://localhost:5000/api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin@123"
}
```

### Use token in headers:
```
Authorization: Bearer <your_jwt_token>
```

### Submit Application:
```
POST http://localhost:5000/api/applications
Authorization: Bearer <token>

{
  "building_name": "Test Building",
  "building_type": "Commercial",
  "address": "123 Main Street",
  "city": "Bhopal",
  "state": "Madhya Pradesh",
  "pincode": "462001",
  "priority_level": "High"
}
```

---

## 🔒 Security Features
- bcrypt password hashing
- JWT token authentication (12-hour expiry)
- Role-based access control
- File type validation on uploads
- SQL injection protection via SQLAlchemy ORM
- CORS enabled for local development

---

## 📊 Database Schema

8 tables: `users`, `applications`, `inspections`, `followups`, `noc`, `documents`, `notifications`, `activity_logs`

All tables have proper foreign keys and relationships.
