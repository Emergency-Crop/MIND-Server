"""
Attractions API Documentation Module

관광지 API 문서화를 위한 설명 및 예시 정의
"""

get_attractions_docs = {
    "summary": "GPS 기반 주변 관광지 목록 조회",
    "description": """
    사용자의 GPS 위치를 기반으로 주변 관광지 목록을 조회합니다.
    TourAPI(한국관광공사)를 통해 관광지 정보를 제공합니다.

    ■ 주요 기능
        • 현재 위치에서 지정한 '반경(km)' 내 검색
        • 카테고리 필터(관광지, 문화시설, 축제, 음식점 등)
        • 거리순/이름순/평점순 정렬
        • 페이지네이션 지원

    ■ 사용 시나리오
        • 여행 앱에서 현재 위치 주변의 관광지 표시
        • 무한 스크롤(페이지네이션) 적용

    ■ API 사용법
        - 기본 (반경 2km)
        GET /api/v1/travel/attractions?lat=37.5665&lng=126.9780&radius=2

        - 페이지네이션(다음 페이지)
        GET /api/v1/travel/attractions?lat=37.5665&lng=126.9780&limit=20&offset=20

    ■ Query Parameters

        파라미터           타입      필수   기본값     설명
        ---------------   -------   ----   --------   -----------------------------------------------
        lat               float      O      -         위도 (33.0~39.0)
        lng               float      O      -         경도 (124.0~132.0)
        radius            int        X     2          검색 반경(km, 최대 20)
        category          string     X     all        카테고리(all/tourist/culture/festival/course/leisure/accommodation/shopping/restaurant)
        sort              string     X     distance   정렬(distance|name|rating)
        limit             int        X     20         한 페이지 결과 수(최대 50)
        offset            int        X     0          시작 오프셋

    ■ 카테고리 매핑표
        클라이언트 요청값    설명           한국관광공사 코드
        ----------------  -------------  -----------------
        all               전체           -
        tourist           관광지         12
        culture           문화시설        14
        festival          축제/행사       15
        course            여행코스        25
        leisure           레포츠         28
        accommodation     숙박           32
        shopping          쇼핑           38
        restaurant        음식점         39

    ■ Rate Limiting
        • 분당 요청: 30회 (IP 주소별)
        • 시간당 요청: 500회 (API 키별)
        • 일일 요청: 5,000회 (API 키별)

    ■ 활용 외부 API
        • 한국관광공사 국문 관광정보 서비스: locationBasedList2
    """,
    "responses": {
        200: {
            "description": "관광지 목록 조회 성공",
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
                                "radius_km": 2,
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
                            "error": "INVALID_COORDINATES",
                            "message": "유효하지 않은 GPS 좌표입니다.",
                            "details": {
                                "lat": "위도는 33.0과 39.0 사이의 값이어야 합니다.",
                                "lng": "경도는 124.0과 132.0 사이의 값이어야 합니다."
                            }
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
                        "message": "요청 한도를 초과했습니다.",
                        "detail": {
                            "limit": "30/minute",
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
                        "status": "INTERNAL_SERVER_ERROR",
                        "message": "서버 내부 오류가 발생했습니다.",
                        "detail": {"error": "예상치 못한 오류가 발생했습니다."}
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
                        "message": "외부 API 연동 오류가 발생했습니다.",
                        "detail": {"error": "TourAPI 서비스가 일시적으로 사용할 수 없습니다."}
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
        }
    }
}
