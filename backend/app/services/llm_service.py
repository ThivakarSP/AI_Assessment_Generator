"""LLM Service - Wrapper for Groq API calls."""

import json
import re
from typing import Optional
from groq import Groq

from app.config import get_settings


class LLMService:
    """Service for interacting with Groq API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key)
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = True
    ) -> dict:
        """
        Generate a response from the LLM.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User message/request
            json_mode: If True, enforces JSON output format
            
        Returns:
            Parsed JSON response from LLM
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            if json_mode:
                messages[1]["content"] += "\n\nIMPORTANT: Respond with valid JSON only, no markdown code blocks."
            
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=messages,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )
            
            content = response.choices[0].message.content.strip()
            
            if json_mode:
                # Clean up any markdown code blocks if present
                if content.startswith("```"):
                    content = re.sub(r'^```(?:json)?\s*', '', content)
                    content = re.sub(r'\s*```$', '', content)
                return json.loads(content)
            return {"content": content}
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {e}")
    
    def is_connected(self) -> bool:
        """Check if LLM service is properly configured and connected."""
        return bool(self.settings.groq_api_key)


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
