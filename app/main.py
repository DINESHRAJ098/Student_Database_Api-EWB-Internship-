from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.config import settings
from app.database import init_db
from app.routers import students_router, ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite tables exist
    init_db()
    yield
    # Shutdown logic if needed in future


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        "Production-ready backend API to manage student records using CRUD operations "
        "backed by SQLite, with an optional Ollama AI extension for natural-language inquiries."
    ),
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(students_router)
app.include_router(ai_router)


@app.get("/", include_in_schema=False)
def root():
    """Redirect root directly to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }
