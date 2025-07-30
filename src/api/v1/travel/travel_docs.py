"""
Travel API Documentation Module

API 문서화를 위한 설명 및 예시 정의
"""

get_attractions_docs = {
    "summary": "GPS 기반 주변 관광지 목록 조회",
    "description": """
    사용자의 GPS 위치를 기반으로 주변 관광지 목록을 조회합니다.

    ■ 주요 기능
        • 현재 위치에서 지정한 반경 내의 관광지 검색
        • 카테고리별 필터링 (관광지, 문화시설, 축제, 음식점 등)
        • 거리순, 이름순, 평점순 정렬
        • 페이지네이션 지원
    
    ■ 사용 시나리오
        • 여행 앱에서 현재 위치 주변의 관광지 표시
        • 특정 카테고리(예: 음식점)만 필터링하여 조회
        • 무한 스크롤을 위한 페이지네이션

    ■ API 사용법
        - 기본 사용 예시
        GET /api/v1/travel/attractions?lat=37.5665&lng=126.9780

        - 고급 사용 예시 (카테고리 필터 + 5km 반경)
        GET /api/v1/travel/attractions?lat=37.5665&lng=126.9780&radius=5&category=restaurant

        - 페이지네이션 예시 (다음 페이지 요청)
        GET /api/v1/travel/attractions?lat=37.5665&lng=126.9780&limit=20&offset=20

    ■ Query Parameters 설명

        파라미터    타입     필수   기본값    설명                          예시
        --------   ------   ----   ------   --------------------------   --------
        lat        float     O      -       위도 (33.0~39.0)             37.5665
        lng        float     O      -       경도 (124.0~132.0)           126.9780
        radius     int       X      2       검색 반경(km, 최대 20)        5
        category   string    X      all     관광지 카테고리               restaurant
        sort       string    X      distance 정렬 방식                    name
        limit      int       X      20      한 페이지 결과 수(최대 50)     20
        offset     int       X      0       시작 위치(페이지네이션)        0

        - 카테고리 옵션
            • all           : 전체
            • tourist       : 관광지
            • culture       : 문화시설
            • festival      : 축제/행사
            • course        : 여행코스
            • leisure       : 레포츠
            • accommodation : 숙박
            • shopping      : 쇼핑
            • restaurant    : 음식점

        - 정렬 옵션
            • distance : 거리순 (가까운 순)
            • name     : 이름순 (가나다순)
            • rating   : 평점순 (높은 순)

    ■ 제한사항
        • 지역 제한: 한국 영역 내에서만 사용 가능 (위도: 33.0~39.0, 경도: 124.0~132.0)
        • Rate Limiting: 분당 30회 제한
        • 최대 검색 반경: 20km
        • 최대 결과 수: 한 번에 최대 50개까지 조회 가능

    ■ 참고사항
        • 별도 인증 없이 사용 가능한 공개 API
        • 한국관광공사 API 데이터를 활용
        • 실시간 운영 상태(is_open)는 참고용이며, 방문 전 확인 필요
        • 이미지(thumbnail)가 없는 경우 null 반환""",
    "responses": {
        200: {
            "description": "주변 관광지 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "정상적으로 처리되었습니다.",
                        "detail": {
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
                        "status": "BAD_REQUEST",
                        "message": "요청 형식이 잘못되었습니다.",
                        "detail": {
                            "error": "위도는 33.0과 39.0 사이의 값이어야 합니다."
                        }
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
                        "message": "요청 횟수가 너무 많습니다. 잠시 후 다시 시도하세요.",
                        "detail": {
                            "retry_after": 45,
                            "reset_time": "2025-07-06T14:31:00+09:00"
                        }
                    }
                }
            }
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {
                        "status": "INTERNAL_ERROR",
                        "message": "서버 내부 오류가 발생했습니다.",
                        "detail": {}
                    }
                }
            }
        },
        502: {
            "description": "외부 API (한국관광공사) 연동 오류",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_GATEWAY",
                        "message": "외부 API 연동 중 오류가 발생했습니다.",
                        "detail": "관광 정보 서비스가 일시적으로 사용 불가능합니다."
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
                        "detail": "관광 정보 서비스의 응답이 지연되고 있습니다."
                    }
                }
            }
        },
        505 : {
            "description": "Tour API 요청 오류(인증키 오류 등)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "TOUR_API_ERROR",
                        "message": "Tour API 요청 중 오류가 발생했습니다.",
                        "detail": {
                            "error": "유효하지 않은 인증키입니다."
                        }
                    }
                }
            }
        }
    }
}