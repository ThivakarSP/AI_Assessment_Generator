"""Base Agent class - Abstract interface for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.services.llm_service import get_llm_service


class BaseAgent(ABC):
    """Abstract base class for AI agents."""
    
    def __init__(self):
        self.llm_service = get_llm_service()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging and identification."""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt that defines the agent's behavior."""
        pass
    
    @abstractmethod
    def format_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Format the user prompt from input data."""
        pass
    
    @abstractmethod
    def parse_output(self, raw_output: Dict[str, Any]) -> Any:
        """Parse and validate the LLM output into structured format."""
        pass
    
    def _grade_to_age(self, grade: int) -> str:
        """Convert grade to approximate age range. Shared helper for all agents."""
        age_start = grade + 5
        age_end = grade + 6
        return f"{age_start}-{age_end}"
    
    async def run(self, input_data: Dict[str, Any]) -> Any:
        """
        Execute the agent with given input.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Parsed and validated output
        """
        user_prompt = self.format_user_prompt(input_data)
        
        raw_output = await self.llm_service.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            json_mode=True
        )
        
        return self.parse_output(raw_output)
