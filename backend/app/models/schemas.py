"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ============== MCQ Schemas ==============

class MCQ(BaseModel):
    """Single Multiple Choice Question."""
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    answer: str


# ============== Generator Agent Schemas ==============

class GeneratorInput(BaseModel):
    """Input for Generator Agent."""
    grade: int = Field(..., ge=1, le=12, description="Grade level (1-12)")
    topic: str = Field(..., min_length=1, max_length=255, description="Topic to generate content for")


class GeneratorOutput(BaseModel):
    """Output from Generator Agent."""
    explanation: str
    mcqs: List[MCQ]


# ============== Reviewer Agent Schemas ==============

class ReviewerInput(BaseModel):
    """Input for Reviewer Agent - the Generator's output plus grade context."""
    grade: int
    content: GeneratorOutput


class ReviewerOutput(BaseModel):
    """Output from Reviewer Agent."""
    status: str = Field(..., pattern="^(pass|fail)$")
    feedback: List[str] = []


# ============== API Request/Response Schemas ==============

class GenerateRequest(BaseModel):
    """Request body for /api/generate endpoint."""
    grade: int = Field(..., ge=1, le=12, description="Grade level (1-12)")
    topic: str = Field(..., min_length=1, max_length=255, description="Topic to generate content for")


class GenerateResponse(BaseModel):
    """Response for /api/generate endpoint."""
    session_id: str
    status: str
    generator_output: GeneratorOutput
    reviewer_output: ReviewerOutput
    was_refined: bool = False
    refined_output: Optional[GeneratorOutput] = None


class SessionResponse(BaseModel):
    """Response for /api/sessions/{id} endpoint."""
    session_id: str
    status: str
    grade: int
    topic: str
    attempts: int
    created_at: datetime


class GenerationDetail(BaseModel):
    """Detail for a single generation attempt."""
    attempt: int
    content: GeneratorOutput
    review: ReviewerOutput


class GenerationsResponse(BaseModel):
    """Response for /api/sessions/{id}/generations endpoint."""
    generations: List[GenerationDetail]


class HealthResponse(BaseModel):
    """Response for /api/health endpoint."""
    status: str
    llm_connected: bool
    db_connected: bool


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
