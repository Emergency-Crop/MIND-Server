"""
Feed API Documentation Module

API 문서화를 위한 설명 및 예시 정의
"""

get_feed_docs = {
    "summary": "사용자 아키타입 기반 피드 조회",
    "description": """
    사용자 ID를 기반으로 해당 사용자의 아키타입을 조회하고, 같은 아키타입을 가진 다른 사용자들의 여행 로그를 피드로 제공합니다.

    ■ 주요 기능
        • 사용자 ID로 프로필 정보 조회 (아키타입 포함)
        • 같은 아키타입을 가진 사용자들의 여행 로그 검색
        • 공개된 여행 로그만 필터링
        • 최신순 정렬 및 페이지네이션 지원
    
    ■ 사용 시나리오
        • 사용자가 로그인 후 개인화된 피드 확인
        • 같은 성향(아키타입)을 가진 사용자들의 여행 경험 공유
        • 여행 영감을 얻기 위한 콘텐츠 탐색
        • 무한 스크롤을 위한 페이지네이션

    ■ API 사용법
        - 기본 사용 예시
        GET /api/v1/feed?user_id=806787d0-2cd7-4b82-98c3-68e0...

                 - 페이지네이션 예시 (다음 페이지 요청)
         GET /api/v1/feed?user_id=806787d0-2cd7-4b82-98c3-68e0...&limit=20&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9

    ■ Query Parameters 설명

                 파라미터    타입     필수   기본값    설명                          예시
         --------   ------   ----   ------   --------------------------   --------
         user_id    string    O      -       사용자 ID (UUID)             806787d0-2cd7-4b82-98c3-68e0...
         limit      int       X      20      한 페이지 결과 수(최대 50)     20
         cursor     string    X      null    다음 페이지 커서(Base64)      eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9

    ■ 커서 기반 페이지네이션 (Cursor-based Pagination) 상세 설명

        📖 Limit (제한 개수)
        • 의미: 한 번에 가져올 데이터의 최대 개수
        • 범위: 1 ~ 50
        • 예시: limit=2 → 최대 2개 데이터만 가져옴
        • 용도: 한 페이지에 표시할 데이터 개수 제한

        📖 Cursor (커서)
        • 의미: 다음 페이지의 시작점을 나타내는 토큰
        • 형식: Base64 인코딩된 JSON (created_at, id 포함)
        • 예시: eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9
        • 용도: 데이터 변경에 안전한 페이지네이션

        📖 커서 기반 페이지네이션 장점
        • ✅ 성능 최고: 인덱스 기반 조회로 빠름
        • ✅ 안정성: 데이터 추가/삭제되어도 중복/누락 없음
        • ✅ 무한 스크롤 최적: 인스타그램, 페이스북 등 대형 서비스 사용
        • ✅ 확장성: 대용량 데이터 처리에 적합

        📖 페이지네이션 사용 예시
        총 5개의 여행 로그가 있을 때:
        
        • 첫 번째 페이지: limit=2, cursor=null
          → 결과: [1번째, 2번째] 데이터
          → meta: has_more=true, next_cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9
        
        • 두 번째 페이지: limit=2, cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9
          → 결과: [3번째, 4번째] 데이터
          → meta: has_more=true, next_cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9
        
        • 세 번째 페이지: limit=2, cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9
          → 결과: [5번째] 데이터
          → meta: has_more=false, next_cursor=null

                 📖 실제 API 호출 예시
         GET /feed?user_id=xxx&limit=2                    # 첫 번째 페이지
         GET /feed?user_id=xxx&limit=2&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9   # 두 번째 페이지

    ■ 응답 데이터 구조

        필드 그룹        주요 정보
        ------------   --------------------------
        meta           user_profile, total_count, pagination 정보
        items          TravelLogItemDTO 목록 (여행 로그들)

    ■ 아키타입 설명
        • adventurer    : 모험가 - 새로운 경험을 추구하는 여행자
        • 고요한 회복러 : 평화로운 휴식을 선호하는 여행자
        • 기타 아키타입들...

    ■ 제한사항
        • Rate Limiting: 분당 60회 제한
        • 최대 결과 수: 한 번에 최대 50개까지 조회 가능
        • 공개된 여행 로그만 조회 가능
        • 존재하지 않는 사용자 ID의 경우 404 에러 반환

    ■ 참고사항
        • Supabase 데이터베이스와 연동
        • 사용자 프로필과 여행 로그 테이블 조인 조회
        • 아키타입 기반 개인화된 콘텐츠 제공
        • 최신 작성순으로 정렬됨""",
    "responses": {
        200: {
            "description": "피드 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "정상적으로 처리되었습니다.",
                        "detail": {
                            "meta": {
                                "user_profile": {
                                    "id": "806787d0-2cd7-4b82-98c3-68e0...",
                                    "archetype": "adventurer",
                                    "display_name": "r1h2w3",
                                    "profile_image_url": None,
                                    "bio": "새로운 여행을 시작하는 모험가입니다."
                                },
                                "total_count": 15,
                                "current_count": 3,
                                "limit": 3,
                                "has_more": True,
                                "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9"
                            },
                                                         "items": [
                                 {
                                     "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                     "created_at": "2025-08-13T10:43:26.540889+00:00"
                                 },
                                 {
                                     "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
                                     "created_at": "2025-08-13T07:51:34.857736+00:00"
                                 },
                                 {
                                     "id": "c3d4e5f6-g7h8-9012-cdef-345678901234",
                                     "created_at": "2025-08-13T07:35:24.514219+00:00"
                                 }
                             ]
                        }
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청 (유효하지 않은 사용자 ID, 파라미터 범위 초과)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_REQUEST",
                        "message": "요청 형식이 잘못되었습니다.",
                        "detail": {
                            "error": "유효하지 않은 사용자 ID입니다."
                        }
                    }
                }
            }
        },
        404: {
            "description": "존재하지 않는 사용자",
            "content": {
                "application/json": {
                    "example": {
                        "status": "NOT_FOUND",
                        "message": "존재하지 않는 사용자입니다.",
                        "detail": {
                            "user_id": "00000000-0000-0000-0000-000000000000"
                        }
                    }
                }
            }
        },
        429: {
            "description": "요청 한도 초과 (분당 60회)",
            "content": {
                "application/json": {
                    "example": {
                        "status": "TOO_MANY_REQUESTS",
                        "message": "요청 횟수가 너무 많습니다. 잠시 후 다시 시도하세요.",
                        "detail": {
                            "retry_after": 30,
                            "reset_time": "2025-08-30T02:30:00+09:00"
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
            "description": "데이터베이스 연동 오류",
            "content": {
                "application/json": {
                    "example": {
                        "status": "BAD_GATEWAY",
                        "message": "데이터베이스 연동 중 오류가 발생했습니다.",
                        "detail": "Supabase 연결에 실패했습니다."
                    }
                }
            }
        }
    }
}
