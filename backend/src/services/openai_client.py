
import openai
from functools import lru_cache
from src.settings import settings

@lru_cache(maxsize=1)
def get_openai():
    """Configure the OpenAI client for Azure and return the module (acts like a singleton)."""
    openai.api_key = settings.azure_openai_key
    openai.azure_endpoint = settings.azure_openai_endpoint
    openai.api_version = "2024-05-01-preview"
    return openai
