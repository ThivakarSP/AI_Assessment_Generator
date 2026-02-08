"""Reviewer Agent - Validates educational content for quality and age-appropriateness."""

from typing import Any, Dict
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.models.schemas import ReviewerOutput, GeneratorOutput


class ReviewerAgent(BaseAgent):
    """Agent that reviews generated content for quality and appropriateness."""
    
    def __init__(self):
        super().__init__()
        self._system_prompt = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """Load the system prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "reviewer_prompt.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return self._default_prompt()
    
    def _default_prompt(self) -> str:
        """Fallback prompt if file not found."""
        return """You are an educational content reviewer. Evaluate content for age-appropriateness and accuracy.
        Respond with JSON: {"status": "pass" or "fail", "feedback": ["..."]}"""
    
    @property
    def name(self) -> str:
        return "Reviewer Agent"
    
    @property
    def system_prompt(self) -> str:
        return self._system_prompt
    
    def format_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Format the user prompt with grade and content to review."""
        grade = input_data.get("grade", 5)
        content = input_data.get("content", {})
        
        # Handle both dict and GeneratorOutput
        if isinstance(content, GeneratorOutput):
            content_dict = content.model_dump()
        else:
            content_dict = content
        
        prompt = f"""Review the following educational content generated for Grade {grade} students (ages {self._grade_to_age(grade)}):

## Content to Review

### Explanation:
{content_dict.get('explanation', '')}

### MCQs:
{self._format_mcqs(content_dict.get('mcqs', []))}

## Your Task
1. Evaluate if the language and concepts are appropriate for Grade {grade}
2. Check all facts for accuracy
3. Verify MCQ quality (correct answers, good distractors)
4. Assess clarity and engagement

Provide your review decision (pass/fail) and specific feedback."""

        return prompt
    
    def _format_mcqs(self, mcqs: list) -> str:
        """Format MCQs for review prompt."""
        if not mcqs:
            return "No MCQs provided"
        
        formatted = []
        for i, mcq in enumerate(mcqs, 1):
            # Handle both dict and MCQ object
            if hasattr(mcq, 'question'):
                question = mcq.question
                options = mcq.options
                answer = mcq.answer
            else:
                question = mcq.get('question', '')
                options = mcq.get('options', [])
                answer = mcq.get('answer', '')
            
            opts = "\n".join(f"   {chr(65+j)}. {opt}" for j, opt in enumerate(options))
            formatted.append(f"Q{i}: {question}\n{opts}\n   Answer: {answer}")
        
        return "\n\n".join(formatted)
    
    def parse_output(self, raw_output: Dict[str, Any]) -> ReviewerOutput:
        """Parse and validate the LLM output."""
        try:
            status = raw_output.get("status", "fail").lower()
            
            # Normalize status
            if status not in ["pass", "fail"]:
                status = "fail"
            
            feedback = raw_output.get("feedback", [])
            
            # Ensure feedback is a list
            if isinstance(feedback, str):
                feedback = [feedback] if feedback else []
            
            return ReviewerOutput(
                status=status,
                feedback=feedback
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Reviewer output: {e}")
