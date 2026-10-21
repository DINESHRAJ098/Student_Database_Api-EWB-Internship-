from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import httpx
from app.database import get_db
from app.config import settings
from app.schemas import AIQueryRequest, AIQueryResponse
from app.ai_service import answer_student_query

router = APIRouter(prefix="/ai", tags=["AI Extension (Ollama)"])


@router.post(
    "/query",
    response_model=AIQueryResponse,
    summary="Ask a question about students via Ollama AI",
    description=(
        "Answers natural-language questions (e.g., 'How many students are there?', "
        "'List students born after 2005') by securely extracting database records "
        "and grounding a local Ollama LLM prompt."
    )
)
async def ask_question(request: AIQueryRequest, db: Session = Depends(get_db)):
    result = await answer_student_query(
        db=db,
        question=request.question,
        model=request.model
    )
    return result


@router.get(
    "/status",
    summary="Check Ollama service status and available models",
    description="Probes the local Ollama daemon to check connectivity and list locally installed models."
)
async def check_ollama_status():
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "ollama_connected": True,
                    "ollama_base_url": settings.OLLAMA_BASE_URL,
                    "default_model": settings.OLLAMA_MODEL,
                    "available_models": models
                }
            return {
                "ollama_connected": False,
                "detail": f"Ollama HTTP {response.status_code}: {response.text}"
            }
    except Exception as exc:
        return {
            "ollama_connected": False,
            "ollama_base_url": settings.OLLAMA_BASE_URL,
            "default_model": settings.OLLAMA_MODEL,
            "detail": f"Could not reach Ollama: {str(exc)}"
        }
