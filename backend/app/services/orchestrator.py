"""Orchestrator Service - Coordinates the Generator and Reviewer agent pipeline."""

from typing import Optional
from sqlalchemy.orm import Session as DBSession

from app.agents import GeneratorAgent, ReviewerAgent
from app.models.schemas import (
    GeneratorInput, GeneratorOutput,
    ReviewerOutput, GenerateResponse
)
from app.models.db_models import Session, Generation, Review
from app.config import get_settings


class Orchestrator:
    """Coordinates the content generation and review pipeline."""
    
    def __init__(self, db: DBSession):
        self.db = db
        self.settings = get_settings()
        self.generator = GeneratorAgent()
        self.reviewer = ReviewerAgent()
    
    async def generate_content(
        self,
        grade: int,
        topic: str
    ) -> GenerateResponse:
        """
        Run the full generation pipeline.
        
        1. Create session
        2. Run Generator Agent
        3. Run Reviewer Agent
        4. If fail, retry Generator with feedback (max 1 retry)
        5. Return complete response
        """
        # Create session
        session = Session(
            grade=grade,
            topic=topic,
            status="processing"
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        try:
            # First generation attempt
            generator_output = await self._run_generator(
                session_id=session.id,
                grade=grade,
                topic=topic,
                attempt=1
            )
            
            # Review the generated content
            reviewer_output = await self._run_reviewer(
                session_id=session.id,
                generation_id=self._last_generation_id,
                grade=grade,
                content=generator_output
            )
            
            refined_output: Optional[GeneratorOutput] = None
            was_refined = False
            final_generator_output = generator_output
            final_reviewer_output = reviewer_output
            
            # If review failed and we can retry
            if (reviewer_output.status == "fail" and 
                session.total_attempts < self.settings.max_refinement_attempts + 1):
                
                # Prepare feedback for retry
                feedback = "\n".join(reviewer_output.feedback)
                
                # Retry generation with feedback
                refined_output = await self._run_generator(
                    session_id=session.id,
                    grade=grade,
                    topic=topic,
                    attempt=2,
                    feedback=feedback
                )
                
                # Review the refined content
                final_reviewer_output = await self._run_reviewer(
                    session_id=session.id,
                    generation_id=self._last_generation_id,
                    grade=grade,
                    content=refined_output
                )
                
                was_refined = True
                final_generator_output = refined_output
            
            # Update session status
            session.status = "completed"
            self.db.commit()
            
            return GenerateResponse(
                session_id=session.id,
                status="completed",
                generator_output=generator_output,
                reviewer_output=reviewer_output,
                was_refined=was_refined,
                refined_output=refined_output
            )
            
        except Exception as e:
            session.status = "failed"
            self.db.commit()
            raise e
    
    async def _run_generator(
        self,
        session_id: str,
        grade: int,
        topic: str,
        attempt: int,
        feedback: Optional[str] = None
    ) -> GeneratorOutput:
        """Run the Generator Agent and store results."""
        # Prepare input
        input_data = {
            "grade": grade,
            "topic": topic,
            "feedback": feedback
        }
        
        # Run agent
        output: GeneratorOutput = await self.generator.run(input_data)
        
        # Store in database
        generation = Generation(
            session_id=session_id,
            attempt_number=attempt,
            explanation=output.explanation,
            mcqs=[mcq.model_dump() for mcq in output.mcqs],
            raw_response=output.model_dump(),
            feedback_used=feedback
        )
        self.db.add(generation)
        
        # Update session attempt count
        session = self.db.query(Session).filter(Session.id == session_id).first()
        session.total_attempts = attempt
        self.db.commit()
        self.db.refresh(generation)
        
        self._last_generation_id = generation.id
        
        return output
    
    async def _run_reviewer(
        self,
        session_id: str,
        generation_id: str,
        grade: int,
        content: GeneratorOutput
    ) -> ReviewerOutput:
        """Run the Reviewer Agent and store results."""
        # Prepare input
        input_data = {
            "grade": grade,
            "content": content
        }
        
        # Run agent
        output: ReviewerOutput = await self.reviewer.run(input_data)
        
        # Store in database
        review = Review(
            generation_id=generation_id,
            status=output.status,
            feedback=output.feedback
        )
        self.db.add(review)
        self.db.commit()
        
        return output
