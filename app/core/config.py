from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Saudi Aramco AI Digital Assistant"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "your-secret-key"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/aramco_ai"
    
    # Model Paths (On-premises)
    WHISPER_MODEL_PATH: str = "large-v3"  # Changed from "base" to "large-v3"
    LLM_MODEL_PATH: str = "/data/models/llama-3-8b-instruct" # This is for local file path, Ollama uses LLM_MODEL_NAME
    TTS_MODEL_PATH: str = "/data/models/coqui-tts-xtts-v2"
    
    # Ollama Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    LLM_MODEL_NAME: str = "llama3:8b"

    # API URLs for Mock Integrations (or real ones)
    AAMER_API_URL: str = "http://localhost:8000/api/v1/mocks/aamer"
    CRM_API_URL: str = "http://localhost:8000/api/v1/mocks/crm"
    MYCOMMUNITY_API_URL: str = "http://localhost:8000/api/v1/mocks/mycommunity"
    SISCO_API_URL: str = "http://localhost:8000/api/v1/mocks/sisco"
    PBX_HOST: str = "localhost"
    PBX_PORT: int = 5060

    # Thresholds
    LATENCY_THRESHOLD_MS: int = 700
    
    class Config:
        env_file = ".env"

settings = Settings()
