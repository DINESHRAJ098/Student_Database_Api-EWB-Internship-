# 🎓 Students Database CRUD Application (+ Optional AI Extension)

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-orange.svg)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An industry-standard Python backend application designed to manage student records with persistent **SQLite** storage and **FastAPI**. It includes full Create, Read, Update, and Delete (**CRUD**) operations, strict Pydantic data validation, pagination, multi-field filtering, and an optional **Local AI Assistant powered by Ollama** for natural-language inquiries grounded in verified database records.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture & Design](#-architecture--design)
- [Student Record Schema](#-student-record-schema)
- [API Endpoints](#-api-endpoints)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Database Seeding](#-database-seeding)
- [Running the Application](#-running-the-application)
- [API Documentation (Swagger & ReDoc)](#-api-documentation)
- [Sample Requests & Testing (cURL)](#-sample-requests--testing-curl)
- [Optional Bonus: Local AI with Ollama](#-optional-bonus-local-ai-with-ollama)
- [Running Automated Tests](#-running-automated-tests)
- [Project Review Checklist](#-project-review-checklist)
- [GitHub Submission Guide](#-github-submission-guide)

---

## 🎯 Project Overview

This project was built to fulfill the **EWB Edu Tech Pvt. Ltd. Internship Project Assignment**.

### Key Highlights:
1. **Full CRUD Lifecycle**: Add, retrieve, filter, partially/fully update, and delete student records.
2. **Persistent SQLite Storage**: Backed by **SQLAlchemy ORM** with thread-safe connection pooling.
3. **Data Validation & Error Handling**: Comprehensive validation for email formatting, realistic past dates of birth, phone sanitization, non-empty names, unique constraint enforcement, and custom 400/404/422 responses.
4. **Flexible Querying & Filtering**: Filter students by search keywords, specific course, birth year, plus `skip` and `limit` pagination.
5. **Dual Identifier Lookup**: Endpoints accept both primary key IDs (`/students/1`) and human-readable student codes (`/students/STU-2001`).
6. **Optional Ollama AI Extension**: Answers natural language questions like *"How many students are there?"* or *"List students born after 2005"* strictly grounded in real database context to prevent hallucinations and unrestricted SQL execution.

---

## 🏗 Architecture & Design

```
Python_project/
├── app/
│   ├── __init__.py           # Package indicator
│   ├── config.py             # Settings via Pydantic Settings (.env support)
│   ├── database.py           # SQLite engine, SessionLocal, init_db()
│   ├── models.py             # SQLAlchemy ORM Student model
│   ├── schemas.py            # Pydantic schemas (Base, Create, Update, Response, AI)
│   ├── crud.py               # Database queries, updates, and filters
│   ├── ai_service.py         # Grounded Ollama integration and fallback logic
│   ├── main.py               # FastAPI app, CORS, lifespan startup
│   └── routers/
│       ├── __init__.py       # Routers export
│       ├── students.py       # CRUD endpoints (/students)
│       └── ai.py             # AI inquiry & health endpoints (/ai)
├── tests/
│   ├── __init__.py
│   └── test_api.py           # Full pytest suite with isolated in-memory DB
├── seed_data.py              # Script to populate realistic dummy student data
├── requirements.txt          # Production and testing dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns for Python, SQLite & venv
└── README.md                 # Complete documentation and run instructions
```

---

## 📋 Student Record Schema

Each student profile stores the following fields:

| Field | Type | Required | Description | Constraints / Validation |
| :--- | :--- | :---: | :--- | :--- |
| `id` | Integer | Auto | Internal Primary Key | Autoincrementing index |
| `student_id` | String(50) | Optional / Auto | Unique student identifier | Auto-generated (e.g. `STU-1001`) if omitted |
| `name` | String(100) | Yes | Full name | Non-empty, 1-100 characters |
| `date_of_birth`| Date | Yes | Date of birth | Valid past date, realistic age (≤ 120 yrs) |
| `email` | String(120) | Yes | Student email | Valid RFC-standard email, unique |
| `phone` | String(30) | Optional | Contact phone number | Valid characters (`+0-9() -`) |
| `course` | String(100) | Optional | Course or department | e.g. "Computer Science" |
| `address` | String(255) | Optional | Residential address | e.g. "12 Park Street, Bangalore" |
| `enrollment_date`| Date | Optional | Date of admission | Defaults to current date if omitted |
| `created_at` | DateTime | Auto | Record creation timestamp | Server-generated timestamp |
| `updated_at` | DateTime | Auto | Last modification timestamp | Automatically updated on edits |

---

## 🌐 API Endpoints

| HTTP Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :---: |
| `POST` | `/students` | Create a new student record | `201 Created` |
| `GET` | `/students` | List all students (supports search, course, birth year, pagination) | `200 OK` |
| `GET` | `/students/{student_id}` | Retrieve student by ID or `student_id` code | `200 OK` / `404 Not Found` |
| `PUT` | `/students/{student_id}` | Complete update of a student record | `200 OK` / `404 Not Found` |
| `PATCH` | `/students/{student_id}` | Partial update of student details | `200 OK` / `404 Not Found` |
| `DELETE` | `/students/{student_id}` | Remove a student record permanently | `200 OK` / `404 Not Found` |
| `POST` | `/ai/query` | Natural language question answered via Ollama | `200 OK` |
| `GET` | `/ai/status` | Check local Ollama connection and installed models | `200 OK` |
| `GET` | `/health` | System health check | `200 OK` |

---

## ⚙️ Prerequisites

- **Python 3.10+** (Tested with Python 3.11.4)
- **Git**
- *(Optional)* **Ollama** (Required only for the local AI extension)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration points to local SQLite file `./students.db` and default Ollama port `http://localhost:11434`.

---

## 📦 Database Seeding

To quickly populate the SQLite database with realistic sample student records (covering varied courses and birth years):
```bash
python seed_data.py
```
*Output:*
```text
Initializing database tables...
Successfully seeded database! Added 6 new records. Total students: 6
```

---

## 🏃 Running the Application

Launch the FastAPI development server using **Uvicorn**:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- **API Base URL**: `http://127.0.0.1:8000`
- **Swagger UI Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Alternative UI**: `http://127.0.0.1:8000/redoc`

---

## 📖 API Documentation

FastAPI provides an automatic, interactive UI where you can test every endpoint directly in your browser:
- Navigate to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- Click on any route, click **"Try it out"**, fill in sample parameters, and click **"Execute"**.

---

## 🧪 Sample Requests & Testing (cURL)

### 1. Create a Student (POST `/students`)
```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arjun Kumar",
    "date_of_birth": "2005-06-18",
    "email": "arjun.kumar@example.com",
    "phone": "+91 98765 01234",
    "course": "Computer Science",
    "address": "15 MG Road, Bangalore, KA"
  }'
```

### 2. List All Students (GET `/students`)
```bash
curl -X GET "http://127.0.0.1:8000/students"
```

### 3. Filter Students by Course and Pagination
```bash
curl -X GET "http://127.0.0.1:8000/students?course=Computer%20Science&limit=10&skip=0"
```

### 4. Filter Students Born After 2005
```bash
curl -X GET "http://127.0.0.1:8000/students?birth_year_after=2005"
```

### 5. View Single Student by Identifier (GET `/students/{student_id}`)
```bash
curl -X GET "http://127.0.0.1:8000/students/STU-2001"
# OR by numeric ID:
curl -X GET "http://127.0.0.1:8000/students/1"
```

### 6. Partial Update (PATCH `/students/{student_id}`)
```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU-2001" \
  -H "Content-Type: application/json" \
  -d '{
    "course": "Artificial Intelligence & Data Science",
    "phone": "+91 99999 88888"
  }'
```

### 7. Delete a Student (DELETE `/students/{student_id}`)
```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU-2001"
```

---

## 🤖 Optional Bonus: Local AI with Ollama

The application features a secure, grounded AI inquiry endpoint that connects to a local **Ollama** model.

### Security & Architecture
- **No Unrestricted SQL**: The LLM is never given direct SQL execution privileges.
- **Grounded Context**: The backend extracts clean, structured student records from SQLite and provides them as system context to the model.
- **Hallucination Prevention**: The model is instructed to answer strictly based on provided records.
- **Graceful Fallback**: If Ollama is offline or uninstalled, the endpoint automatically catches connection errors and returns a direct summary from SQLite without crashing.

### Using Ollama

1. **Install Ollama**: Download from [ollama.com](https://ollama.com/) if not already installed.
2. **Pull a Model**:
   ```bash
   ollama pull llama3.2:1b
   # or use an existing local model such as gemma4:12b
   ```
3. **Check AI Status**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/ai/status"
   ```
4. **Ask Questions via AI**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/ai/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "How many students are enrolled in Computer Science?"
     }'
   ```
   **Example Questions:**
   - *"How many total students are in the database?"*
   - *"List students born after 2005 and their enrolled courses."*
   - *"Which students are residing in Bangalore?"*

---

## 🚦 Running Automated Tests

A comprehensive **pytest** suite verifies all requirements, including full CRUD, edge-case validations, and error handling. Tests use an isolated in-memory SQLite database to preserve production data.

Run the test suite:
```bash
pytest -v
```

Expected output:
```text
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_create_student_with_auto_id PASSED
tests/test_api.py::test_create_student_with_custom_id PASSED
tests/test_api.py::test_create_student_duplicate_email PASSED
tests/test_api.py::test_create_student_duplicate_student_id PASSED
tests/test_api.py::test_create_student_invalid_future_dob PASSED
tests/test_api.py::test_create_student_empty_name PASSED
tests/test_api.py::test_list_students_and_filtering PASSED
tests/test_api.py::test_get_student_by_id_and_student_id PASSED
tests/test_api.py::test_get_nonexistent_student PASSED
tests/test_api.py::test_update_student_patch PASSED
tests/test_api.py::test_update_student_put PASSED
tests/test_api.py::test_update_nonexistent_student PASSED
tests/test_api.py::test_delete_student PASSED
tests/test_api.py::test_delete_nonexistent_student PASSED
tests/test_api.py::test_ai_status_endpoint PASSED
tests/test_api.py::test_ai_query_with_grounded_fallback PASSED
============================= 17 passed in 0.85s ==============================
```

---

## ✅ Project Review Checklist

- [x] **Create**: Add new student records with unique IDs and emails.
- [x] **Read**: List all students, retrieve individual profiles by ID or code, and filter by course / year / search keyword.
- [x] **Update**: Full (`PUT`) and partial (`PATCH`) updates with conflict detection.
- [x] **Delete**: Remove records cleanly with proper HTTP responses.
- [x] **SQLite Persistence**: Relational storage managed via SQLAlchemy ORM.
- [x] **Validation & Error Handling**: Pydantic models preventing invalid dates, malformed emails, and invalid phone numbers.
- [x] **Reproducibility**: Clear instructions, virtualenv configuration, and `requirements.txt`.
- [x] **AI Extension (Bonus)**: Safe, grounded natural language queries via local Ollama.

---

## 📤 GitHub Submission Guide

Follow these steps to submit your project:

1. **Verify Git Status**:
   ```bash
   git status
   ```
2. **Stage and Commit all Files**:
   ```bash
   git add .
   git commit -m "feat: complete student database CRUD API with SQLite and Ollama AI extension"
   ```
3. **Link Your Remote GitHub Repository**:
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
4. **Submit**: Copy your public GitHub repository URL and submit it via the designated EWB submission channel.
