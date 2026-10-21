from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student")
    date_of_birth: date = Field(..., description="Student's date of birth (YYYY-MM-DD)")
    email: EmailStr = Field(..., description="Unique email address of the student")
    phone: Optional[str] = Field(None, max_length=30, description="Contact phone number")
    course: Optional[str] = Field(None, max_length=100, description="Course enrolled in")
    address: Optional[str] = Field(None, max_length=255, description="Residential address")
    enrollment_date: Optional[date] = Field(default_factory=date.today, description="Date enrolled (YYYY-MM-DD)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Student name cannot be empty or only whitespace.")
        return clean

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        today = date.today()
        if value >= today:
            raise ValueError("Date of birth must be in the past.")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age > 120:
            raise ValueError("Date of birth indicates an age exceeding realistic bounds (max 120 years).")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        clean = value.strip()
        if not clean:
            return None
        # Allow numbers, dashes, spaces, plus sign, brackets
        allowed = set("+0123456789- ()")
        if not all(c in allowed for c in clean):
            raise ValueError("Phone number contains invalid characters.")
        return clean


class StudentCreate(StudentBase):
    student_id: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Optional custom student ID. If omitted, one will be generated automatically (e.g. STU-1001)."
    )

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        clean = value.strip()
        if not clean:
            return None
        return clean


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        clean = value.strip()
        if not clean:
            raise ValueError("Student name cannot be empty or only whitespace.")
        return clean

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: Optional[date]) -> Optional[date]:
        if value is None:
            return None
        today = date.today()
        if value >= today:
            raise ValueError("Date of birth must be in the past.")
        return value


class StudentResponse(StudentBase):
    id: int
    student_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language question about student records")
    model: Optional[str] = Field(None, description="Optional override for the Ollama model to use")


class AIQueryResponse(BaseModel):
    question: str
    answer: str
    model_used: str
    records_consulted: int
    context_summary: Optional[str] = None
