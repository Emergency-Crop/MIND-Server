"""
Health DTO 모듈

- Health Check 응답 스키마 정의
"""

from pydantic import Field
from src.library.dto import BaseDTO
from typing import Dict, Optional


class HealthReadDTO(BaseDTO):
    """
    Health Check 응답용 DTO
    """
    status: str = Field(..., description="서버 상태", example="healthy")
    message: str = Field(..., description="상태 메시지", example="Server is running normally")
    timestamp: str = Field(..., description="응답 시간 (ISO 8601 형식)", example="2025-01-03T10:30:00Z")
    version: str = Field(..., description="API 버전 정보", example="1.0.0")
    services: Optional[Dict[str, str]] = Field(None, description="연동 서비스별 상태 정보", example={
        "server": "available"
    })
