"""
travel API Documentation Module

API 문서화를 위한 설명 및 예시 정의
"""

get_attractions_docs = {
    "summary": "GPS 기반 주변 관광지 목록 조회",
    "description": """
    사용자의 GPS 위치를 기반으로 주변 관광지 목록을 조회합니다.
    
    **주요 기능**:
    - 현재 위치에서 지정한 반경 내의 관광지 검색
    - 카테고리별 필터링 (관광지, 문화시설, 축제, 음식점 등)
    - 거리순, 이름순, 평점순 정렬
    - 페이지네이션 지원
    
    **사용 시나리오**:
    - 여행 앱에서 현재 위치 주변의 관광지 표시
    - 특정 카테고리(예: 음식점)만 필터링하여 조회
    - 무한 스크롤을 위한 페이지네이션
    
    **제한사항**:
    - 한국 영역 내에서만 사용 가능 (위도: 33.0~39.0, 경도: 124.0~132.0)
    - Rate limiting: 분당 30회 제한
    - 최대 검색 반경: 20km
    
    **참고사항**:
    - 별도 인증 없이 사용 가능한 공개 API
    - 한국관광공사 API 데이터를 활용
    - 실시간 운영 상태는 참고용이며, 방문 전 확인 필요
    """,
    "responses": {
        200: {
            "description": "주변 관광지 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "주변 관광지 조회가 완료되었습니다.",
                        "data": {
                            "meta": {
                                "search_location": {
                                    "lat": 37.5665,
                                    "lng": 126.9780
                                },
                                "radius_km": 5,
                                "category": "전체",
                                "sort": "거리순",
                                "pagination": {
                                    "total_count": 157,
                                    "current_count": 20,
                                    "limit": 20,
                                    "offset": 0,
                                    "has_more": True,
                                    "next_offset": 20
                                }
                            },
                            "items": [
                                {
                                    "id": "126508",
                                    "type": "tourist",
                                    "type_name": "관광지",
                                    "name": "경복궁",
                                    "thumbnail": "https://tong.visitkorea.or.kr/cms/resource/83/2678083_image3_1.JPG",
                                    "address": "서울특별시 종로구 사직로 161",
                                    "distance_m": 1250,
                                    "distance_text": "1.3km",
                                    "rating": 4.6,
                                    "is_open": True
                                },
                                {
                                    "id": "264122",
                                    "type": "tourist",
                                    "type_name": "관광지",
                                    "name": "북촌한옥마을",
                                    "thumbnail": "https://tong.visitkorea.or.kr/cms/resource/12/2641122_image2_1.JPG",
                                    "address": "서울특별시 종로구 계동길 37",
                                    "distance_m": 1850,
                                    "distance_text": "1.9km",
                                    "rating": 4.3,
                                    "is_open": True
                                }
                            ]
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 (GPS 좌표 오류, 파라미터 범위 초과)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "INVALID_COORDINATES",
                            "message": "유효하지 않은 GPS 좌표입니다.",
                            "details": {
                                "lat": "위도는 33.0과 39.0 사이의 값이어야 합니다.",
                                "lng": "경도는 124.0과 132.0 사이의 값이어야 합니다."
                            }
                        },
                        "timestamp": "2025-07-06T14:30:00+09:00"
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과 (분당 30회)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "요청 한도를 초과했습니다.",
                            "details": {
                                "limit": "30/minute",
                                "retry_after": 45,
                                "reset_time": "2025-07-06T14:31:00+09:00"
                            }
                        },
                        "timestamp": "2025-07-06T14:30:00+09:00"
                    }
                }
            }
        },
        500: {
            "description": "서버 내부 오류"
        },
        502: {
            "description": "외부 API (한국관광공사) 연동 오류"
        },
        504: {
            "description": "외부 API 응답 시간 초과"
        }
    }
}