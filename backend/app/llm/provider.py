"""LLM Provider abstraction layer supporting local Ollama models with deterministic fallback."""
import os
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMProvider:
    """Centralized LLM Service supporting local Ollama and robust fallback."""

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3")
        self.timeout = 15.0

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Attempt to call Ollama for structured JSON output. Returns None if LLM is unavailable."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.ollama_base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "")
                    return json.loads(response_text)
        except Exception as e:
            logger.warning(f"Ollama LLM call failed or unavailable ({e}). Using deterministic fallback.")
        return None

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Attempt to call Ollama for raw text output. Returns None if LLM is unavailable."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.ollama_base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama LLM text call failed ({e}). Using deterministic fallback.")
        return None

    async def check_health(self) -> Dict[str, Any]:
        """Check if local LLM service is available."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.ollama_base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "status": "available",
                        "provider": "Ollama",
                        "available_models": models,
                        "current_model": self.model_name,
                        "mode": "REAL_LLM"
                    }
        except Exception:
            pass
        return {
            "status": "unavailable",
            "provider": "Ollama",
            "mode": "DETERMINISTIC_FALLBACK",
            "note": "Deterministic ML models and rule engines active."
        }


# Singleton instance
_llm_provider: Optional[LLMProvider] = None

def get_llm_provider() -> LLMProvider:
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider
