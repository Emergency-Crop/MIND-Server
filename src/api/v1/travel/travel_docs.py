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
                                "radius_km": 2,
                                "category": "전체",
                                "sort": "거리순",
                                "pagination": {
                                    "total_count": 157,
                                    "current_count": 3,
                                    "limit": 3,
                                    "offset": 0,
                                    "has_more": True,
                                    "next_offset": 3
                                }
                            },
                            "items": [
                                {
                                    "id": "523990",
                                    "type": "shopping",
                                    "type_name": "쇼핑",
                                    "name": "진교장 (3, 8일)",
                                    "thumbnail": None,
                                    "address": "서울특별시 중구 세종대로 110 (태평로1가)",
                                    "distance_m": 18,
                                    "distance_text": "18m",
                                    "rating": 4.2,
                                    "is_open": True
                                },
                                {
                                    "id": "523991",
                                    "type": "shopping",
                                    "type_name": "쇼핑",
                                    "name": "옥종장 (3, 8일)",
                                    "thumbnail": None,
                                    "address": "서울특별시 중구 세종대로 110 (태평로1가)",
                                    "distance_m": 18,
                                    "distance_text": "18m",
                                    "rating": 4.1,
                                    "is_open": True
                                },
                                {
                                    "id": "130183",
                                    "type": "culture",
                                    "type_name": "문화시설",
                                    "name": "서울도서관",
                                    "thumbnail": None,
                                    "address": "서울특별시 중구 세종대로 110 (태평로1가)",
                                    "distance_m": 68,
                                    "distance_text": "68m",
                                    "rating": 4.6,
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

get_attraction_detail_docs = {
    "summary": "특정 관광지 상세 정보 조회",
    "description": """
    특정 관광지의 상세 정보를 조회합니다.

    ■ 주요 기능
        • 관광지의 모든 상세 정보 제공 (기본 정보, 이미지, 위치, 연락처, 운영 정보 등)
        • 편의시설 정보 (주차, 휠체어 접근, 유모차, 반려동물 등)
        • 주변 관광지 추천 (반경 2km 이내, 최대 5개)
        • 방문 팁 및 교통 정보 제공
        • 태그 기반 검색/필터링 지원

    ■ 사용 시나리오
        • 관광지 상세 페이지에서 모든 정보 표시
        • 방문 계획 수립을 위한 상세 정보 확인
        • 주변 관광지 연계 추천
        • 접근성 정보를 통한 포용적 여행 정보 제공

    ■ API 사용법
        - 기본 사용 예시
        GET /api/v1/travel/attractions/130183

        - 서울도서관 상세 정보 조회
        GET /api/v1/travel/attractions/130183

    ■ Path Parameters 설명

        파라미터    타입     필수   설명                          예시
        --------   ------   ----   --------------------------   --------
        content_id string    O     관광지 고유 ID               130183

    ■ 응답 데이터 구조

        필드 그룹        주요 정보
        ------------   --------------------------
        기본 정보       id, name, type, summary, description
        이미지 정보     main_image, images (최대 10개)
        위치 정보       address, coordinates (lat, lng)
        연락처 정보     phone, website
        운영 정보       rating, is_open, opening_hours, admission_fee
        편의시설        parking, facilities (접근성 정보)
        부가 정보       tags, tips, nearby_attractions
        교통 정보       transportation (지하철, 버스, 주차)

    ■ 제한사항
        • Rate Limiting: 분당 30회 제한
        • 한국 내 관광지 정보만 제공
        • 이미지가 없는 경우 기본 이미지 제공
        • 실시간 운영 상태는 참고용 (방문 전 확인 필요)

    ■ 참고사항
        • 별도 인증 없이 사용 가능한 공개 API
        • 한국관광공사 API 데이터를 활용
        • 클라이언트에서 바로 사용 가능한 형태로 가공된 데이터
        • 주변 관광지는 자동으로 계산되어 제공됨""",
    "responses": {
        200: {
            "description": "관광지 상세 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "정상적으로 처리되었습니다.",
                        "detail": {
                            "id": "130183",
                            "name": "서울도서관",
                            "type": "culture",
                            "type_name": "문화시설",
                            "summary": "서울도서관에 대한 상세 정보입니다.",
                            "description": "서울도서관에 대한 상세 정보가 제공되지 않습니다. 방문 전 전화로 문의하시기 바랍니다.",
                            "main_image": "https://via.placeholder.com/400x300?text=No+Image",
                            "images": [
                                "https://via.placeholder.com/400x300?text=No+Image"
                            ],
                            "address": "서울특별시 중구 세종대로 110 (태평로1가)",
                            "coordinates": {
                                "lat": 37.5665986816,
                                "lng": 126.9783710306
                            },
                            "phone": "",
                            "website": None,
                            "rating": 4.6,
                            "is_open": True,
                            "opening_hours": "정보 없음",
                            "closed_days": "정보 없음",
                            "admission_fee": "정보 없음",
                            "parking": None,
                            "facilities": None,
                            "tags": [
                                "문화시설",
                                "관광지"
                            ],
                            "tips": [
                                "방문 전 전화로 문의하시기 바랍니다."
                            ],
                            "nearby_attractions": [
                                {
                                    "id": "523990",
                                    "name": "진교장 (3, 8일)",
                                    "distance_m": 18,
                                    "distance_text": "18m"
                                },
                                {
                                    "id": "523991",
                                    "name": "옥종장 (3, 8일)",
                                    "distance_m": 18,
                                    "distance_text": "18m"
                                },
                                {
                                    "id": "630793",
                                    "name": "대한민국청소년미디어대전",
                                    "distance_m": 68,
                                    "distance_text": "68m"
                                },
                                {
                                    "id": "128968",
                                    "name": "서울광장",
                                    "distance_m": 127,
                                    "distance_text": "127m"
                                },
                                {
                                    "id": "126509",
                                    "name": "덕수궁",
                                    "distance_m": 307,
                                    "distance_text": "307m"
                                }
                            ],
                            "transportation": None
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 (유효하지 않은 contentId)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_REQUEST",
                        "message": "요청 형식이 잘못되었습니다.",
                        "detail": {
                            "error": "유효하지 않은 관광지 ID입니다."
                        }
                    }
                }
            }
        },
        404: {
            "description": "존재하지 않는 관광지 ID",
            "content": {
                "application/json": {
                    "example": {
                        "status": "NOT_FOUND",
                        "message": "존재하지 않는 관광지입니다.",
                        "detail": {
                            "content_id": "3067187"
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
        }
    }
}

get_weather_docs = {
    "summary": "GPS 기반 현재 날씨 정보 조회",
    "description": """
    사용자의 GPS 위치를 기반으로 현재 날씨 정보를 조회합니다.

    ■ 주요 기능
        • 현재 위치의 실시간 날씨 정보 제공
        • 기온, 습도, 강수량, 풍속, 풍향 등 상세 정보
        • 여행 적합성 자동 판단 및 조언 제공
        • 날씨 상태별 이모지 아이콘 제공
    
    ■ 사용 시나리오
        • 여행 앱에서 현재 위치의 날씨 정보 표시
        • 여행 계획 수립 시 날씨 고려
        • 실시간 날씨 기반 여행 조언 제공

    ■ API 사용법
        - 기본 사용 예시
        GET /api/v1/travel/weather?lat=37.5665&lng=126.9780

    ■ Query Parameters 설명

        파라미터    타입     필수   설명                          예시
        --------   ------   ----   --------------------------   --------
        lat        float     O     위도 (33.0~39.0)             37.5665
        lng        float     O     경도 (124.0~132.0)           126.9780

    ■ 응답 데이터 설명

        필드명                    타입     설명
        ----------------------   ------   --------------------------
        location                 object   위치 정보
        ├── lat                 float    요청된 위도
        ├── lng                 float    요청된 경도
        └── area_name           string   지역명 (시/도 시/군/구)
        
        current                  object   현재 날씨 정보
        ├── temperature         float    기온 (섭씨, °C)
        ├── temperature_text    string   기온 표시용 텍스트
        ├── humidity            int      습도 (%)
        ├── humidity_text       string   습도 표시용 텍스트
        ├── precipitation       float    1시간 강수량 (mm)
        ├── precipitation_text  string   강수 표시용 텍스트
        ├── wind_speed          float    풍속 (m/s)
        ├── wind_direction      int      풍향 (도, 0-360)
        ├── wind_text           string   바람 표시용 텍스트
        ├── condition           string   날씨 상태 (한글)
        ├── condition_code      string   날씨 상태 코드 (영문)
        └── icon                string   날씨 아이콘 (이모지)
        
        updated_at              string   마지막 업데이트 시간 (ISO 8601)
        is_travel_friendly      boolean  여행 적합 여부
        travel_advice           string   여행 관련 조언

    ■ 날씨 상태 코드표

        condition_code    condition    icon    설명
        --------------    ---------    ----    ----
        clear            맑음         ☀️     맑은 날씨
        partly_cloudy    구름조금     ⛅     구름이 조금 있음
        cloudy           흐림         ☁️     흐린 날씨
        rain             비           🌧️     비가 오는 날씨
        snow             눈           ❄️     눈이 오는 날씨
        rain_snow        비/눈        🌨️     비와 눈이 함께

    ■ 제한사항
        • 지역 제한: 한국 영역 내에서만 사용 가능 (위도: 33.0~39.0, 경도: 124.0~132.0)
        • Rate Limiting: 분당 60회 제한
        • 데이터 업데이트: 매시 40분에 발표 (10분마다 업데이트)

    ■ 참고사항
        • 별도 인증 없이 사용 가능한 공개 유틸리티 API
        • 한국관광공사 TourAPI의 기상청 단기예보 조회서비스(초단기실황) 데이터 활용
        • 여행 적합성은 기온, 강수량, 풍속을 종합하여 판단
        • 주요 관광지는 미리 호출하여 캐싱 처리하는 방법도 추천""",
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
                                "area_name": "서울특별시 중구"
                            },
                            "current": {
                                "temperature": 15.2,
                                "temperature_text": "15°",
                                "humidity": 65,
                                "humidity_text": "65%",
                                "precipitation": 0.0,
                                "precipitation_text": "강수없음",
                                "wind_speed": 3.2,
                                "wind_direction": 230,
                                "wind_text": "남서풍 3.2m/s",
                                "condition": "맑음",
                                "condition_code": "clear",
                                "icon": "☀️"
                            },
                            "updated_at": "2025-01-06T14:00:00+09:00",
                            "is_travel_friendly": True,
                            "travel_advice": "여행하기 좋은 날씨입니다"
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_REQUEST",
                        "message": "잘못된 요청입니다.",
                        "detail": {
                            "error": "유효하지 않은 GPS 좌표입니다."
                        }
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과",
            "content": {
                "application/json": {
                    "example": {
                        "status": "TOO_MANY_REQUESTS",
                        "message": "요청 한도를 초과했습니다.",
                        "detail": {
                            "limit": "60/minute",
                            "retry_after": 30
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
                        "detail": "날씨 정보 조회 중 오류가 발생했습니다"
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
                        "message": "외부 서비스 연동 중 오류가 발생했습니다.",
                        "detail": "기상청 API 연동 중 오류가 발생했습니다"
                    }
                }
            }
        },
        503: {
            "description": "서비스 일시적 장애",
            "content": {
                "application/json": {
                    "example": {
                        "status": "SERVICE_UNAVAILABLE",
                        "message": "서비스를 일시적으로 사용할 수 없습니다.",
                        "detail": "기상청 API 일시적 장애"
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
                        "message": "외부 서비스 응답 시간이 초과되었습니다.",
                        "detail": "기상청 API 응답 시간 초과"
                    }
                }
            }
        }
    }
}