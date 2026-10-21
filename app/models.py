from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True, default=date.today)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, student_id='{self.student_id}', name='{self.name}', course='{self.course}')>"
