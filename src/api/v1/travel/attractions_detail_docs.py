"""
Attractions Detail API Documentation

관광지 상세 정보 조회 API의 OpenAPI 문서 정의
"""

get_attraction_detail_docs = {
    "description": """
    특정 관광지의 상세 정보를 조회합니다.
    
    ## 주요 기능
    
    - **종합 정보 제공**: 기본 정보, 이미지, 위치, 연락처, 운영 정보를 한 번에 제공
    - **편의시설 정보**: 주차, 휠체어 접근, 유모차, 반려동물, 와이파이 등 접근성 정보
    - **실용적 정보**: 방문 팁, 주변 관광지, 교통 정보 등 실제 여행에 필요한 정보
    - **이미지 보장**: 이미지가 없는 경우 기본 이미지 제공
    
    ## 데이터 품질
    
    - **실시간 정보**: TourAPI를 통한 최신 관광지 정보
    - **검증된 데이터**: 이미지 URL 검증 및 기본값 제공
    - **사용자 친화적**: HTML 태그 제거, 텍스트 정리, 일관된 형식
    
    ## 성능 최적화
    
    - **병렬 API 호출**: 공통정보, 소개정보, 이미지정보를 동시에 조회
    - **선택적 조회**: 주변 관광지는 필요시에만 조회
    - **캐싱**: 30분간 상세 정보 캐싱으로 응답 속도 향상
    """,
    "responses": {
        200: {
            "description": "관광지 상세 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "요청이 성공적으로 처리되었습니다.",
                        "detail": {
                            "success": True,
                            "message": "관광지 상세 정보 조회가 완료되었습니다.",
                            "data": {
                                "id": "126508",
                                "name": "경복궁",
                                "type": "tourist_spot",
                                "type_name": "관광지",
                                "summary": "조선 왕조의 법궁으로 1395년 태조 이성계에 의해 창건된 대표적인 고궁",
                                "description": "조선 왕조의 법궁인 경복궁은 1395년 태조 이성계에 의해 창건되었습니다. 경복궁은 동궐(창덕궁)이나 서궐(경희궁)에 비해 위치상 북궐이라 불렸습니다. 근정전, 경회루, 향원정 등 아름다운 건축물들이 조화를 이루고 있습니다...",
                                "main_image": "https://tong.visitkorea.or.kr/cms/resource/83/2678083_image3_1.JPG",
                                "images": [
                                    "https://tong.visitkorea.or.kr/cms/resource/83/2678083_image3_1.JPG",
                                    "https://tong.visitkorea.or.kr/cms/resource/84/2678084_image3_1.JPG",
                                    "https://tong.visitkorea.or.kr/cms/resource/85/2678085_image3_1.JPG"
                                ],
                                "address": "서울특별시 종로구 사직로 161",
                                "coordinates": {
                                    "lat": 37.5796,
                                    "lng": 126.9770
                                },
                                "phone": "02-3700-3900",
                                "website": "https://www.royalpalace.go.kr",
                                "rating": 4.6,
                                "is_open": True,
                                "opening_hours": "09:00~18:00 (동절기 09:00~17:00)",
                                "closed_days": "화요일",
                                "admission_fee": "성인 3,000원, 청소년·어린이 1,500원",
                                "parking": {
                                    "available": True,
                                    "fee": "유료",
                                    "info": "경복궁 주차장 이용 가능"
                                },
                                "facilities": {
                                    "wheelchair_accessible": True,
                                    "stroller_friendly": True,
                                    "pet_allowed": False,
                                    "wifi": True,
                                    "restaurant": True,
                                    "gift_shop": True
                                },
                                "tags": [
                                    "궁궐",
                                    "문화재",
                                    "사적",
                                    "역사",
                                    "전통건축",
                                    "포토스팟"
                                ],
                                "tips": [
                                    "수문장 교대식은 10:00, 14:00, 15:00에 진행됩니다",
                                    "경회루와 향원정은 특별관람 신청 시 내부 관람 가능합니다",
                                    "한복 착용 시 무료 입장이 가능합니다"
                                ],
                                "nearby_attractions": [
                                    {
                                        "id": "264122",
                                        "name": "북촌한옥마을",
                                        "distance_m": 800,
                                        "distance_text": "800m"
                                    },
                                    {
                                        "id": "126535",
                                        "name": "인사동",
                                        "distance_m": 1200,
                                        "distance_text": "1.2km"
                                    }
                                ],
                                "transportation": {
                                    "subway": [
                                        "3호선 경복궁역 5번 출구 (도보 3분)",
                                        "5호선 광화문역 2번 출구 (도보 5분)"
                                    ],
                                    "bus": [
                                        "간선버스: 109, 171, 272",
                                        "지선버스: 1020, 7025"
                                    ],
                                    "parking_info": "경복궁 주차장 이용 (유료)"
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 - 유효하지 않은 contentId",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_REQUEST",
                        "message": "잘못된 요청입니다.",
                        "detail": {
                            "error": "INVALID_CONTENT_ID",
                            "message": "유효하지 않은 관광지 ID입니다.",
                            "details": {
                                "content_id": "invalid_id"
                            }
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
                        "message": "요청한 리소스를 찾을 수 없습니다.",
                        "detail": {
                            "error": "ATTRACTION_NOT_FOUND",
                            "message": "존재하지 않는 관광지입니다.",
                            "details": {
                                "content_id": "999999"
                            }
                        }
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과 - 분당 30회",
            "content": {
                "application/json": {
                    "example": {
                        "status": "TOO_MANY_REQUESTS",
                        "message": "요청 한도를 초과했습니다.",
                        "detail": {
                            "error": "RATE_LIMIT_EXCEEDED",
                            "message": "요청 한도를 초과했습니다.",
                            "details": {
                                "limit": "30/minute",
                                "retry_after": 45,
                                "reset_time": "2025-07-06T14:31:00+09:00"
                            }
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
                        "detail": {
                            "error": "INTERNAL_SERVER_ERROR",
                            "message": "서버 내부 오류가 발생했습니다."
                        }
                    }
                }
            }
        },
        502: {
            "description": "외부 API 연동 오류 - 한국관광공사 API 오류",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_GATEWAY",
                        "message": "외부 서비스와의 통신에 실패했습니다.",
                        "detail": {
                            "error": "TOUR_API_ERROR",
                            "message": "TourAPI 오류: 서비스 일시 중단"
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
                        "message": "요청 시간이 초과되었습니다.",
                        "detail": {
                            "error": "GATEWAY_TIMEOUT",
                            "message": "외부 API 응답 시간 초과"
                        }
                    }
                }
            }
        }
    }
}
