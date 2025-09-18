"""
Weather API Documentation Module

날씨 API 문서화를 위한 설명 및 예시 정의
"""

get_weather_docs = {
    "summary": "GPS 기반 현재 날씨 정보 조회",
    "description": """
    사용자의 GPS 위치를 기반으로 현재 날씨 정보를 조회합니다.

    ■ 주요 기능
        • GPS 좌표 기반 현재 날씨 정보 제공
        • 기온, 습도, 강수량, 풍속, 풍향 정보
        • 날씨 상태 및 아이콘 제공
        • 여행 적합성 판단 및 조언

    ■ 사용 시나리오
        • 여행 앱에서 현재 위치의 날씨 정보 표시
        • 여행 계획 수립 시 날씨 고려

    ■ API 사용법
        GET /api/v1/travel/weather?lat=37.5665&lng=126.9780

    ■ Query Parameters
        파라미터   타입    필수   설명                예시
        --------  -----   ----  ------------------  -------
        lat       float    O    위도 (33.0~39.0)     37.5665
        lng       float    O    경도 (124.0~132.0)   126.9780

    ■ 제한사항
        • Rate Limiting: 분당 30회 제한
        • 한국 내 위치만 지원
        • 실시간 데이터 제공 (10분마다 업데이트)
    """,
    "responses": {
        200: {
            "description": "날씨 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "정상적으로 처리되었습니다.",
                        "detail": {
                            "location": {
                                "lat": 37.5665,
                                "lng": 126.9780,
                                "area_name": "서울특별시"
                            },
                            "current": {
                                "temperature": 22.5,
                                "temperature_text": "23°",
                                "humidity": 65,
                                "humidity_text": "65%",
                                "precipitation": 0.0,
                                "precipitation_text": "강수없음",
                                "wind_speed": 2.3,
                                "wind_direction": 180,
                                "wind_text": "남풍 2.3m/s",
                                "condition": "맑음",
                                "condition_code": "clear",
                                "icon": "☀️"
                            },
                            "updated_at": "2025-01-06T15:30:00+09:00",
                            "is_travel_friendly": True,
                            "travel_advice": "여행하기 좋은 날씨입니다."
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 (GPS 좌표 오류)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_REQUEST",
                        "message": "요청 형식이 잘못되었습니다.",
                        "detail": {"error": "유효하지 않은 GPS 좌표입니다."}
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과 (분당 30회)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "TOO_MANY_REQUESTS",
                        "message": "요청 한도를 초과했습니다.",
                        "detail": {"limit": "30/minute", "retry_after": 45}
                    }
                }
            }
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {
                        "status": "INTERNAL_SERVER_ERROR",
                        "message": "서버 내부 오류가 발생했습니다.",
                        "detail": {"error": "예상치 못한 오류가 발생했습니다."}
                    }
                }
            }
        },
        502: {
            "description": "외부 API 연동 오류",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_GATEWAY",
                        "message": "외부 API 연동 오류가 발생했습니다.",
                        "detail": {"error": "기상청 API 서비스가 일시적으로 사용할 수 없습니다."}
                    }
                }
            }
        },
        504: {
            "description": "외부 API 응답 시간 초과",
            "content": {
                "application/json": {
                    "example": {
                        "status": "GATEWAY_TIMEOUT",
                        "message": "외부 API 응답 시간이 초과되었습니다.",
                        "detail": "기상청 API의 응답이 지연되고 있습니다."
                    }
                }
            }
        }
    }
}
