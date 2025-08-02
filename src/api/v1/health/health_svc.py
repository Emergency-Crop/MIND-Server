"""
Health Service Module

- 서버 상태 및 외부 서비스 연동 상태 확인 로직
"""
from datetime import datetime
from typing import Dict, Optional
from src.core.logger import get_logger

_logger = get_logger(__name__)


async def check_external_services() -> Dict[str, str]:
    """
    외부 서비스들의 상태를 확인합니다.
    """
    services = {}
    
    # 서버 자체 상태만 확인
    services["server"] = "available"
    _logger.info("Server is available")
    
    return services


async def get_health_status() -> Optional[Dict]:
    """
    서버의 전체적인 상태를 확인하고 딕셔너리를 반환합니다.
    """
    # 외부 서비스 상태 확인
    services = await check_external_services()
    
    # 전체 상태 판단 (모든 서비스가 available이면 healthy)
    all_healthy = all(status == "available" for status in services.values())
    
    # 현재 시간을 ISO 8601 형식으로 변환
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "message": "Server is running normally" if all_healthy else "Some services are unavailable",
        "timestamp": timestamp,
        "version": "1.0.0",
        "services": services
    }
