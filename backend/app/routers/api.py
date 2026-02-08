"""API Routes for the AI Assessment application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session as DBSession

from app.models.database import get_db
from app.models.db_models import Session, Generation, Review
from app.models.schemas import (
    GenerateRequest, GenerateResponse,
    SessionResponse, GenerationsResponse, GenerationDetail,
    HealthResponse, ErrorResponse,
    GeneratorOutput, ReviewerOutput, MCQ
)
from app.services.orchestrator import Orchestrator
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    db: DBSession = Depends(get_db)
):
    """
    Generate educational content for a given grade and topic.
    
    This endpoint:
    1. Runs the Generator Agent to create content
    2. Runs the Reviewer Agent to validate content
    3. If review fails, retries once with feedback
    4. Returns all agent outputs for transparency
    """
    try:
        orchestrator = Orchestrator(db)
        result = await orchestrator.generate_content(
            grade=request.grade,
            topic=request.topic
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: DBSession = Depends(get_db)
):
    """Get the status of a content generation session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        grade=session.grade,
        topic=session.topic,
        attempts=session.total_attempts,
        created_at=session.created_at
    )


@router.get("/sessions/{session_id}/generations", response_model=GenerationsResponse)
async def get_session_generations(
    session_id: str,
    db: DBSession = Depends(get_db)
):
    """Get all generation attempts for a session."""
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    generations = db.query(Generation).filter(
        Generation.session_id == session_id
    ).order_by(Generation.attempt_number).all()
    
    results = []
    for gen in generations:
        # Reconstruct GeneratorOutput
        mcqs = [MCQ(**mcq) for mcq in (gen.mcqs or [])]
        content = GeneratorOutput(
            explanation=gen.explanation or "",
            mcqs=mcqs
        )
        
        # Get review for this generation
        review = db.query(Review).filter(Review.generation_id == gen.id).first()
        review_output = ReviewerOutput(
            status=review.status if review else "pending",
            feedback=review.feedback if review else []
        )
        
        results.append(GenerationDetail(
            attempt=gen.attempt_number,
            content=content,
            review=review_output
        ))
    
    return GenerationsResponse(generations=results)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: DBSession = Depends(get_db)):
    """Check the health of the application."""
    # Check LLM connection
    llm_service = get_llm_service()
    llm_connected = llm_service.is_connected()
    
    # Check DB connection
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
    
    return HealthResponse(
        status="healthy" if (llm_connected and db_connected) else "degraded",
        llm_connected=llm_connected,
        db_connected=db_connected
    )
