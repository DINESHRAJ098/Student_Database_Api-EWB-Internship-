import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Student

logger = logging.getLogger("ai_service")


def get_database_grounding_context(db: Session, max_records: int = 100) -> Dict[str, Any]:
    """
    Safely retrieves student records from the database in Python code.
    Prevents unrestricted SQL execution while providing clean grounding context.
    """
    total_count = db.query(Student).count()
    records = db.query(Student).order_by(Student.id.asc()).limit(max_records).all()

    student_data = []
    courses = set()
    for s in records:
        if s.course:
            courses.add(s.course)
        student_data.append({
            "student_id": s.student_id,
            "name": s.name,
            "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else None,
            "course": s.course,
            "enrollment_date": s.enrollment_date.isoformat() if s.enrollment_date else None,
            "email": s.email,
            "phone": s.phone
        })

    return {
        "total_count": total_count,
        "courses_available": sorted(list(courses)),
        "students": student_data
    }


async def query_ollama(
    prompt: str,
    system_prompt: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends prompt with grounded system context to a local Ollama instance.
    Returns the response or an informative error/fallback.
    """
    target_model = model or settings.OLLAMA_MODEL
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"

    payload = {
        "model": target_model,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "answer": data.get("response", "").strip(),
                    "model": target_model
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama returned HTTP status {response.status_code}: {response.text}",
                    "model": target_model
                }
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Could not connect to Ollama at {settings.OLLAMA_BASE_URL}. Please ensure Ollama is running ('ollama serve' or desktop app).",
            "model": target_model
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": f"Ollama request timed out after {settings.OLLAMA_TIMEOUT_SECONDS}s. Try a lighter model like llama3.2:1b.",
            "model": target_model
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Unexpected error while querying Ollama: {str(exc)}",
            "model": target_model
        }


async def answer_student_query(
    db: Session,
    question: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Grounds the user's natural language query using database records and queries Ollama.
    """
    context = get_database_grounding_context(db)
    students_json = json.dumps(context["students"], indent=2)

    system_prompt = (
        "You are an intelligent, helpful student database assistant for an educational institution.\n"
        "Your task is to answer questions strictly grounded on the student records provided below.\n"
        "CRITICAL RULES:\n"
        "1. Only use facts from the provided context.\n"
        "2. Do not invent or assume data that is not in the context.\n"
        "3. If the context does not contain the answer, say 'Based on the current database records, this information is not available.'\n"
        "4. Be concise, polite, and accurate.\n\n"
        f"DATABASE CONTEXT:\n"
        f"- Total registered students: {context['total_count']}\n"
        f"- Active courses: {', '.join(context['courses_available']) if context['courses_available'] else 'None'}\n"
        f"- Student Records:\n{students_json}\n"
    )

    ollama_res = await query_ollama(prompt=question, system_prompt=system_prompt, model=model)

    if ollama_res["success"]:
        answer = ollama_res["answer"]
        model_used = ollama_res["model"]
    else:
        # Fallback explanation if Ollama isn't active
        err_msg = ollama_res["error"]
        answer = (
            f"[AI Service Notice]: {err_msg}\n\n"
            f"Direct Database Summary:\n"
            f"• Total Students in Database: {context['total_count']}\n"
            f"• Available Courses: {', '.join(context['courses_available']) if context['courses_available'] else 'None'}\n"
            f"• Records Loaded for Context: {len(context['students'])}"
        )
        model_used = ollama_res["model"]

    return {
        "question": question,
        "answer": answer,
        "model_used": model_used,
        "records_consulted": len(context["students"]),
        "context_summary": f"Total records: {context['total_count']}, Courses: {len(context['courses_available'])}"
    }
