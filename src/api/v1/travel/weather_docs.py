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
        • 고가용성 Fallback 시스템 (Circuit Breaker 패턴)
        • 기상청 API 장애 시 자동 모의 데이터 제공

    ■ 사용 시나리오
        • 여행 앱에서 현재 위치의 날씨 정보 표시
        • 여행 계획 수립 시 날씨 고려
        • 외부 API 장애 상황에서도 안정적인 서비스 제공

    ■ API 사용법
        GET /api/v1/travel/weather?lat=37.5665&lng=126.9780

    ■ Query Parameters
        파라미터   타입    필수   설명                예시
        --------  -----   ----  ------------------  -------
        lat       float    O    위도 (33.0~39.0)     37.5665
        lng       float    O    경도 (124.0~132.0)   126.9780

    ■ 고가용성 시스템
        • Circuit Breaker: 3회 연속 실패 시 5분간 API 호출 건너뛰기
        • 빠른 타임아웃: 5초 내 응답 없으면 즉시 Fallback
        • 지능형 모의 데이터: 시간대별/계절별 고려한 합리적 데이터
        • 투명한 Fallback: 사용자는 실제/모의 데이터 구분 불가

    ■ Fallback 시스템 동작 방식
        1. 기상청 API 호출 시도 (5초 타임아웃)
        2. 실패 시 → Circuit Breaker 실패 카운트 증가
        3. 3회 연속 실패 → 5분간 Circuit Breaker 활성화
        4. Circuit Breaker 활성화 중 → 즉시 모의 데이터 제공
        5. 5분 후 → 자동으로 API 재시도
        6. API 복구 시 → 자동으로 실제 데이터 사용

    ■ 모의 데이터 특징
        • 시간대별 온도: 새벽(15°C), 오전(20°C), 오후(25°C), 저녁(18°C)
        • 자연스러운 변동: ±3°C 랜덤 변동
        • 합리적인 범위: 습도 40-80%, 풍속 1-5m/s
        • 기상청 API와 동일한 응답 구조

    ■ 제한사항
        • Rate Limiting: 분당 30회 제한
        • 한국 내 위치만 지원
        • 실시간 데이터 제공 (10분마다 업데이트)
        • 기상청 API 장애 시 모의 데이터 자동 제공
    """,
    "responses": {
        200: {
            "description": "날씨 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "요청이 성공적으로 처리되었습니다.",
                        "detail": {
                            "success": True,
                            "message": "현재 날씨 조회가 완료되었습니다.",
                            "data": {
                                "source": {
                                    "provider": "KMA",
                                    "api": "getUltraSrtNcst",
                                    "baseDate": "20251022",
                                    "baseTime": "0900",
                                    "nx": 60,
                                    "ny": 127,
                                    "served_at": "2025-10-22T09:30:00+09:00",
                                    "note": "매 정시 생성, 정시+10분부터 제공"
                                },
                                "location": {
                                    "lat": 37.5665,
                                    "lng": 126.9780,
                                    "area_name": "서울특별시 중구",
                                    "admin": {
                                        "level1": "서울특별시",
                                        "level2": "중구",
                                        "level3": "명동",
                                        "code": "1114055000",
                                        "nx": 60,
                                        "ny": 127,
                                        "match_source": "grid+nearest",
                                        "distance_m": 150.2,
                                        "confidence": 0.85
                                    }
                                },
                                "current": {
                                    "temperature": 22.5,
                                    "temperature_text": "22.5°C",
                                    "humidity": 65,
                                    "humidity_text": "65%",
                                    "precipitation_1h": 0.0,
                                    "precipitation_text": "강수없음",
                                    "wind_speed": 2.3,
                                    "wind_speed_text": "2.3 m/s",
                                    "wind_direction_deg": 180,
                                    "wind_direction_16": "S",
                                    "wind_direction_text": "남풍",
                                    "wind_strength_text": "약함",
                                    "condition_pty_code": 0,
                                    "condition_pty_text": "강수없음",
                                    "condition_sky_code": None,
                                    "condition_sky_text": None,
                                    "icon": "⛅"
                                },
                                "raw": None,
                                "derived": {
                                    "is_travel_friendly": True,
                                    "travel_advice": "날씨가 맑고 선선합니다. 야외 활동하기 좋은 날씨예요."
                                },
                                "updated_at": "2025-10-22T09:30:00+09:00"
                            }
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
            "description": "외부 API 연동 오류 (Circuit Breaker 비활성화 시에만 발생)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_GATEWAY",
                        "message": "외부 API 연동 중 오류가 발생했습니다.",
                        "detail": {
                            "error": "TIMEOUT",
                            "message": "기상청 API 응답 시간 초과"
                        }
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
