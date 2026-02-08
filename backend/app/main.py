"""FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.database import init_db
from app.routers.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    yield
    # Shutdown (cleanup if needed)


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title="AI Assessment API",
    description="AI-powered educational content generation with Generator and Reviewer agents",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ai-assessment-generator.vercel.app"
    ] if settings.environment == "development" else [
        "https://ai-assessment-generator.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Assessment API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
