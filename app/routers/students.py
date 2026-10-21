from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
import app.crud as crud

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student record",
    description="Creates a new student. A unique student_id will be auto-generated if not provided."
)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    # Check if student with this email already exists
    if crud.get_student_by_email(db, student_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with email '{student_in.email}' already exists."
        )

    # Check if custom student_id was provided and already exists
    if student_in.student_id:
        if crud.get_student_by_student_id(db, student_in.student_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with student_id '{student_in.student_id}' already exists."
            )

    return crud.create_student(db, student_in)


@router.get(
    "",
    response_model=List[StudentResponse],
    summary="List and filter students",
    description="Retrieve students with optional filters: search query, course name, birth year, and pagination."
)
def list_students(
    search: Optional[str] = Query(None, description="Search by name, email, student ID, or course"),
    course: Optional[str] = Query(None, description="Filter by course name"),
    birth_year_after: Optional[int] = Query(None, description="Filter students born strictly after this year"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    return crud.get_students(
        db=db,
        search=search,
        course=course,
        birth_year_after=birth_year_after,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get a student by ID",
    description="Retrieve student details using either their primary key ID or unique string student_id (e.g. STU-1001)."
)
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Full update of student details",
    description="Update an existing student's details completely."
)
def update_student_put(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' not found."
        )

    # Check for email conflict if email is updated
    if student_update.email and student_update.email != student.email:
        existing = crud.get_student_by_email(db, student_update.email)
        if existing and existing.id != student.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with email '{student_update.email}' already exists."
            )

    return crud.update_student(db, student, student_update)


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Partial update of student details",
    description="Partially modify one or more fields of an existing student."
)
def update_student_patch(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' not found."
        )

    # Check for email conflict if email is updated
    if student_update.email and student_update.email != student.email:
        existing = crud.get_student_by_email(db, student_update.email)
        if existing and existing.id != student.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with email '{student_update.email}' already exists."
            )

    return crud.update_student(db, student, student_update)


@router.delete(
    "/{student_id}",
    summary="Delete a student",
    description="Remove a student record permanently from the database."
)
def delete_student(student_id: str, db: Session = Depends(get_db)):
    student = crud.get_student_by_identifier(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with identifier '{student_id}' not found."
        )

    crud.delete_student(db, student)
    return {
        "status": "success",
        "message": f"Student '{student.name}' (ID: {student.student_id}) successfully deleted."
    }
