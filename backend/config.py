from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application Settings
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    DATABASE_URL: str = "sqlite:///./amida_assistant.db"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "https://localhost:8000/api/auth/google/callback"
    
    # Slack OAuth
    SLACK_CLIENT_ID: Optional[str] = None
    SLACK_CLIENT_SECRET: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    SLACK_REDIRECT_URI: str = "https://localhost:8000/api/auth/slack/callback"
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    class Config:
        env_file = ".env"


settings = Settings()
