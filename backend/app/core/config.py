import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "ReachOut SMB"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./reachout.db"

    # Supabase
    SUPABASE_URL: str = "https://mock.supabase.co"
    SUPABASE_ANON_KEY: str = "mock-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "mock-service-role-key"

    # AI Configuration (Gemini)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Meta Platform (Graph API v26.0 current official supported version)
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_GRAPH_API_VERSION: str = "v26.0"

    # Instagram
    INSTAGRAM_VERIFY_TOKEN: str = "reachout_instagram_verify_token_2026"
    INSTAGRAM_APP_SECRET: Optional[str] = None

    # WhatsApp Cloud API
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: str = "reachout_whatsapp_verify_token_2026"
    WHATSAPP_APP_SECRET: Optional[str] = None

    # Public URLs
    NEXT_PUBLIC_APP_URL: str = "http://localhost:3000"
    BACKEND_PUBLIC_URL: str = "http://localhost:8000"

    # Mock Mode Flags
    MOCK_AI: bool = True
    MOCK_INSTAGRAM: bool = True
    MOCK_WHATSAPP: bool = True
    MOCK_PAYMENTS: bool = True

    # Security / Auth
    JWT_SECRET: str = "reachout-smb-secure-jwt-secret-key-development-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://*.vercel.app"
    ]

settings = Settings()
