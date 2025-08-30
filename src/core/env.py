"""
환경 변수 기반으로 실행 환경에 따라 설정
"""
import os
from pydantic_settings import BaseSettings
from typing import Literal

# 환경 변수
class Env(BaseSettings):
    PYTHONPATH: str = "."
    API_DOC_VIEW: bool = True

    # 데이터베이스 설정
    DB_PROTOCOL: str = "postgresql+asyncpg"
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "db"
    DB_PORT: str = "5432"
    DB_NAME: str

    # 로깅
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_TO_CONSOLE: bool = True
    LOG_ROTATE: bool = False

    # 외부 API 키
    TOUR_API_KEY: str  # 한국관광공사 API 인증키
    OPENAI_API_KEY: str  # OpenAI API 인증키
    
    # Supabase 설정
    SUPABASE_URL: str = "https://hfdkwhyfhfoyfowcbxvl.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhmZGt3aHlmaGZveWZvd2NieHZsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDg0OTgzNywiZXhwIjoyMDY2NDI1ODM3fQ.YHejg7fV2w5hzYbufXIUwRXIvHtVE1vJqyCbbPkT6Vw"
    
    class Config:
        # MODE 값에 따라 다른 env 파일 자동 선택
        env_file = (
            ".env.production"
            if os.getenv("MODE", "development") == "production"
            else ".env"
        )

env = Env()