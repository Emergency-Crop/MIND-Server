# src/api/v1/health/health_docs.py

get_health_docs = {
    "summary": "서버 헬스체크",
    "description": """
    서버의 정상 동작 여부를 확인하는 헬스체크 API입니다.

    - 서버 자체의 상태와 외부 서비스 연동 상태를 확인합니다.
    - 모든 서비스가 정상이면 "healthy" 상태를 반환합니다.
    - 일부 서비스에 문제가 있으면 "unhealthy" 상태를 반환합니다.

    **확인 대상**:
    - 서버 자체 상태

    **권장 사용 시점**:
    - 서버 모니터링 시스템에서 주기적 호출
    - 로드밸런서의 헬스체크
    - 클라이언트 앱에서 서버 상태 확인
    """,
    "responses": {
        200: {
            "description": "서버 상태 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "message": "Server is running normally",
                        "timestamp": "2025-01-03T10:30:00Z",
                        "version": "1.0.0",
                        "services": {
                            "server": "available"
                        }
                    }
                }
            }
        },
        503: {
            "description": "서비스 일시 사용 불가",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "message": "Some services are unavailable",
                        "timestamp": "2025-01-03T10:30:00Z",
                        "version": "1.0.0",
                        "services": {
                            "server": "unavailable"
                        }
                    }
                }
            }
        },
        504: {
            "description": "외부 서비스 연동 타임아웃",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "message": "External service timeout",
                        "timestamp": "2025-01-03T10:30:00Z",
                        "version": "1.0.0",
                        "services": {
                            "server": "timeout"
                        }
                    }
                }
            }
        }
    }
}
