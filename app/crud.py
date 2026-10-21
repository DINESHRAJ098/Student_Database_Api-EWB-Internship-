import random
import string
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def generate_unique_student_id(db: Session, prefix: str = "STU") -> str:
    """Generate a unique human-readable student ID like STU-1001 or STU-ABCD."""
    max_attempts = 10
    for _ in range(max_attempts):
        suffix = "".join(random.choices(string.digits, k=4))
        candidate = f"{prefix}-{suffix}"
        exists = db.query(Student).filter(Student.student_id == candidate).first()
        if not exists:
            return candidate
    # Fallback to random alphanumeric if numeric collision occurs
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


def get_student_by_id(db: Session, student_pk: int) -> Optional[Student]:
    """Retrieve student by primary key ID."""
    return db.query(Student).filter(Student.id == student_pk).first()


def get_student_by_student_id(db: Session, student_id: str) -> Optional[Student]:
    """Retrieve student by unique student_id string."""
    return db.query(Student).filter(Student.student_id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Retrieve student by email address."""
    return db.query(Student).filter(Student.email == email).first()


def get_student_by_identifier(db: Session, identifier: str) -> Optional[Student]:
    """
    Retrieve student by either unique student_id string or integer primary key.
    Allows endpoints like /students/STU-1001 or /students/1.
    """
    # Try exact match on student_id
    student = get_student_by_student_id(db, identifier)
    if student:
        return student

    # If identifier is numeric, try match on primary key id
    if identifier.isdigit():
        return get_student_by_id(db, int(identifier))

    return None


def get_students(
    db: Session,
    search: Optional[str] = None,
    course: Optional[str] = None,
    birth_year_after: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Student]:
    """
    Retrieve students with optional filtering and pagination.
    - search: matches name, email, or student_id
    - course: filters exact course (case-insensitive)
    - birth_year_after: filters students born strictly after the given year
    """
    query = db.query(Student)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.name.ilike(term),
                Student.email.ilike(term),
                Student.student_id.ilike(term),
                Student.course.ilike(term)
            )
        )

    if course:
        query = query.filter(Student.course.ilike(f"%{course.strip()}%"))

    if birth_year_after is not None:
        query = query.filter(extract("year", Student.date_of_birth) > birth_year_after)

    return query.order_by(Student.id.asc()).offset(skip).limit(limit).all()


def count_students(db: Session) -> int:
    """Return total number of students."""
    return db.query(Student).count()


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create and persist a new student record."""
    student_id = student_in.student_id
    if not student_id:
        student_id = generate_unique_student_id(db)

    db_student = Student(
        student_id=student_id,
        name=student_in.name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email,
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=student_in.enrollment_date
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, db_student: Student, update_data: StudentUpdate) -> Student:
    """Update existing student attributes based on non-null fields in StudentUpdate."""
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> None:
    """Delete a student record from the database."""
    db.delete(db_student)
    db.commit()
