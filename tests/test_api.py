from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Create in-memory SQLite database for isolated testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==============================================================================
# Health Check Tests
# ==============================================================================

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ==============================================================================
# CREATE Operation Tests (POST /students)
# ==============================================================================

def test_create_student_with_auto_id():
    payload = {
        "name": "Jane Doe",
        "date_of_birth": "2002-05-14",
        "email": "jane.doe@example.com",
        "phone": "+1 555-0199",
        "course": "Computer Science",
        "address": "123 Campus Lane"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert data["student_id"].startswith("STU-")
    assert "id" in data


def test_create_student_with_custom_id():
    payload = {
        "student_id": "CUSTOM-99",
        "name": "John Smith",
        "date_of_birth": "2001-10-20",
        "email": "john.smith@example.com",
        "phone": "+1 555-0144",
        "course": "Data Analytics"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "CUSTOM-99"


def test_create_student_duplicate_email():
    payload = {
        "name": "Alice",
        "date_of_birth": "2003-01-01",
        "email": "duplicate@example.com"
    }
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/students", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_create_student_duplicate_student_id():
    payload1 = {
        "student_id": "UNIQUE-1",
        "name": "Alice",
        "date_of_birth": "2003-01-01",
        "email": "alice@example.com"
    }
    payload2 = {
        "student_id": "UNIQUE-1",
        "name": "Bob",
        "date_of_birth": "2003-01-01",
        "email": "bob@example.com"
    }
    client.post("/students", json=payload1)
    res = client.post("/students", json=payload2)
    assert res.status_code == 400
    assert "student_id" in res.json()["detail"]


def test_create_student_invalid_future_dob():
    payload = {
        "name": "Time Traveler",
        "date_of_birth": "2099-01-01",
        "email": "future@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_create_student_empty_name():
    payload = {
        "name": "   ",
        "date_of_birth": "2000-01-01",
        "email": "blank@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


# ==============================================================================
# READ Operation Tests (GET /students and GET /students/{id})
# ==============================================================================

def test_list_students_and_filtering():
    # Insert multiple students
    s1 = {"student_id": "STU-01", "name": "Aarav Sharma", "date_of_birth": "2004-03-15", "email": "aarav@example.com", "course": "Computer Science"}
    s2 = {"student_id": "STU-02", "name": "Diya Patel", "date_of_birth": "2006-07-22", "email": "diya@example.com", "course": "AI & ML"}
    s3 = {"student_id": "STU-03", "name": "Rohan Verma", "date_of_birth": "2007-11-05", "email": "rohan@example.com", "course": "Computer Science"}

    client.post("/students", json=s1)
    client.post("/students", json=s2)
    client.post("/students", json=s3)

    # List all
    res = client.get("/students")
    assert res.status_code == 200
    assert len(res.json()) == 3

    # Filter by course
    res_course = client.get("/students?course=Computer%20Science")
    assert res_course.status_code == 200
    assert len(res_course.json()) == 2

    # Filter by search keyword
    res_search = client.get("/students?search=Diya")
    assert res_search.status_code == 200
    assert len(res_search.json()) == 1
    assert res_search.json()[0]["name"] == "Diya Patel"

    # Filter born after 2005
    res_dob = client.get("/students?birth_year_after=2005")
    assert res_dob.status_code == 200
    data_dob = res_dob.json()
    assert len(data_dob) == 2
    for item in data_dob:
        birth_year = int(item["date_of_birth"].split("-")[0])
        assert birth_year > 2005


def test_get_student_by_id_and_student_id():
    payload = {
        "student_id": "STU-XYZ",
        "name": "Maya Singh",
        "date_of_birth": "2003-08-19",
        "email": "maya@example.com",
        "course": "Physics"
    }
    create_res = client.post("/students", json=payload)
    db_id = create_res.json()["id"]

    # Retrieve by string student_id
    res_str = client.get("/students/STU-XYZ")
    assert res_str.status_code == 200
    assert res_str.json()["email"] == "maya@example.com"

    # Retrieve by numeric primary key ID
    res_num = client.get(f"/students/{db_id}")
    assert res_num.status_code == 200
    assert res_num.json()["student_id"] == "STU-XYZ"


def test_get_nonexistent_student():
    response = client.get("/students/NONEXISTENT-999")
    assert response.status_code == 404


# ==============================================================================
# UPDATE Operation Tests (PUT & PATCH /students/{id})
# ==============================================================================

def test_update_student_patch():
    payload = {
        "student_id": "STU-PATCH",
        "name": "Original Name",
        "date_of_birth": "2002-04-10",
        "email": "orig@example.com",
        "course": "Art"
    }
    client.post("/students", json=payload)

    # Partial update course and phone
    patch_payload = {
        "course": "Digital Media",
        "phone": "+1 234-567-8900"
    }
    res = client.patch("/students/STU-PATCH", json=patch_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Original Name"  # Unchanged
    assert data["course"] == "Digital Media"  # Updated
    assert data["phone"] == "+1 234-567-8900"  # Updated


def test_update_student_put():
    payload = {
        "student_id": "STU-PUT",
        "name": "Before Update",
        "date_of_birth": "2000-01-01",
        "email": "before@example.com"
    }
    client.post("/students", json=payload)

    put_payload = {
        "name": "After Update",
        "email": "after@example.com",
        "course": "Robotics"
    }
    res = client.put("/students/STU-PUT", json=put_payload)
    assert res.status_code == 200
    assert res.json()["name"] == "After Update"
    assert res.json()["email"] == "after@example.com"
    assert res.json()["course"] == "Robotics"


def test_update_nonexistent_student():
    response = client.patch("/students/GHOST-ID", json={"name": "Ghost"})
    assert response.status_code == 404


# ==============================================================================
# DELETE Operation Tests (DELETE /students/{id})
# ==============================================================================

def test_delete_student():
    payload = {
        "student_id": "STU-DELETE",
        "name": "To Be Deleted",
        "date_of_birth": "2001-02-03",
        "email": "delete.me@example.com"
    }
    client.post("/students", json=payload)

    # Delete
    del_res = client.delete("/students/STU-DELETE")
    assert del_res.status_code == 200
    assert "successfully deleted" in del_res.json()["message"]

    # Verify deleted
    get_res = client.get("/students/STU-DELETE")
    assert get_res.status_code == 404


def test_delete_nonexistent_student():
    response = client.delete("/students/DOES-NOT-EXIST")
    assert response.status_code == 404


# ==============================================================================
# AI Query & Status Tests
# ==============================================================================

def test_ai_status_endpoint():
    response = client.get("/ai/status")
    assert response.status_code == 200
    assert "ollama_connected" in response.json()


def test_ai_query_with_grounded_fallback():
    # Insert a student so grounding context is populated
    payload = {
        "student_id": "STU-AI",
        "name": "Nikola Tesla",
        "date_of_birth": "2006-07-10",
        "email": "tesla@example.com",
        "course": "Electrical Engineering"
    }
    client.post("/students", json=payload)

    # Query AI endpoint
    ai_req = {"question": "How many students are enrolled?"}
    response = client.post("/ai/query", json=ai_req)
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert data["records_consulted"] >= 1
