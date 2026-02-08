"""Generator Agent - Creates grade-appropriate educational content."""

from typing import Any, Dict
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.models.schemas import GeneratorOutput, MCQ


class GeneratorAgent(BaseAgent):
    """Agent that generates educational content with explanations and MCQs."""
    
    def __init__(self):
        super().__init__()
        self._system_prompt = self._load_prompt()
    
    def _load_prompt(self) -> str:
        """Load the system prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "generator_prompt.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return self._default_prompt()
    
    def _default_prompt(self) -> str:
        """Fallback prompt if file not found."""
        return """You are an educational content generator. Create grade-appropriate explanations and MCQs.
        Respond with JSON: {"explanation": "...", "mcqs": [{"question": "...", "options": [...], "answer": "..."}]}"""
    
    @property
    def name(self) -> str:
        return "Generator Agent"
    
    @property
    def system_prompt(self) -> str:
        return self._system_prompt
    
    def format_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Format the user prompt with grade and topic."""
        grade = input_data.get("grade", 5)
        topic = input_data.get("topic", "")
        feedback = input_data.get("feedback", None)
        
        prompt = f"""Generate educational content for:
- **Grade Level**: {grade} (ages {self._grade_to_age(grade)})
- **Topic**: {topic}

Create:
1. A clear, engaging explanation of the topic appropriate for Grade {grade} students
2. Exactly 5 multiple choice questions to test understanding

Remember to adapt your language and examples to be appropriate for {self._grade_to_age(grade)} year old students."""

        if feedback:
            prompt += f"""

IMPORTANT: This is a RETRY. The previous content was rejected with the following feedback:
{feedback}

Please address these issues in your new response."""
        
        return prompt
    
    def parse_output(self, raw_output: Dict[str, Any]) -> GeneratorOutput:
        """Parse and validate the LLM output."""
        try:
            explanation = raw_output.get("explanation", "")
            mcqs_data = raw_output.get("mcqs", [])
            
            mcqs = []
            for mcq in mcqs_data:
                mcqs.append(MCQ(
                    question=mcq.get("question", ""),
                    options=mcq.get("options", []),
                    answer=mcq.get("answer", "")
                ))
            
            return GeneratorOutput(
                explanation=explanation,
                mcqs=mcqs
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Generator output: {e}")
