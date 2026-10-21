from datetime import date
from app.database import SessionLocal, init_db
from app.models import Student
import app.crud as crud


SAMPLE_STUDENTS = [
    {
        "student_id": "STU-2001",
        "name": "Aarav Sharma",
        "date_of_birth": date(2004, 3, 15),
        "email": "aarav.sharma@example.com",
        "phone": "+91 98765 43210",
        "course": "Computer Science",
        "address": "12 Park Street, Bangalore, KA",
        "enrollment_date": date(2022, 8, 1)
    },
    {
        "student_id": "STU-2002",
        "name": "Diya Patel",
        "date_of_birth": date(2006, 7, 22),
        "email": "diya.patel@example.com",
        "phone": "+91 98123 45678",
        "course": "Artificial Intelligence",
        "address": "45 Lotus Garden, Ahmedabad, GJ",
        "enrollment_date": date(2024, 8, 10)
    },
    {
        "student_id": "STU-2003",
        "name": "Rohan Verma",
        "date_of_birth": date(2005, 11, 5),
        "email": "rohan.verma@example.com",
        "phone": "+91 98345 67890",
        "course": "Data Science",
        "address": "88 Civil Lines, Delhi, DL",
        "enrollment_date": date(2023, 7, 15)
    },
    {
        "student_id": "STU-2004",
        "name": "Ananya Iyer",
        "date_of_birth": date(2007, 1, 30),
        "email": "ananya.iyer@example.com",
        "phone": "+91 98456 78901",
        "course": "Computer Science",
        "address": "14 Marine Drive, Mumbai, MH",
        "enrollment_date": date(2024, 8, 12)
    },
    {
        "student_id": "STU-2005",
        "name": "Kabir Mehta",
        "date_of_birth": date(2003, 9, 18),
        "email": "kabir.mehta@example.com",
        "phone": "+91 98711 22334",
        "course": "Mechanical Engineering",
        "address": "67 Residency Road, Pune, MH",
        "enrollment_date": date(2021, 9, 1)
    },
    {
        "student_id": "STU-2006",
        "name": "Sneha Reddy",
        "date_of_birth": date(2006, 4, 12),
        "email": "sneha.reddy@example.com",
        "phone": "+91 98999 11223",
        "course": "Data Science",
        "address": "22 Jubilee Hills, Hyderabad, TS",
        "enrollment_date": date(2024, 8, 1)
    }
]


def seed():
    print("Initializing database tables...")
    init_db()
    db = SessionLocal()
    try:
        created_count = 0
        for data in SAMPLE_STUDENTS:
            existing = crud.get_student_by_email(db, data["email"])
            if not existing:
                student = Student(**data)
                db.add(student)
                created_count += 1

        db.commit()
        total = crud.count_students(db)
        print(f"Successfully seeded database! Added {created_count} new records. Total students: {total}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
