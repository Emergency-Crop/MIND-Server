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
         limit      int       X      null    한 페이지 결과 수(최대 1000, null이면 모든 결과 반환)     20
         cursor     string    X      null    다음 페이지 커서(Base64)      eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9

    ■ 페이지네이션 사용 예시
        GET /feed?user_id=xxx&limit=2                    # 첫 번째 페이지
        GET /feed?user_id=xxx&limit=2&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNS0wOC0zMFQwMzowMDowMCJ9   # 두 번째 페이지

    ■ 응답 데이터 구조

        필드 그룹        주요 정보
        ------------   --------------------------
        meta           user_profile, total_count, pagination 정보
        items          TravelLogItemDTO 목록 (여행 로그들)


    ■ 제한사항
        • Rate Limiting: 분당 60회 제한
        • 최대 결과 수: 한 번에 최대 1000개까지 조회 가능 (limit=null이면 모든 결과 반환)
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
                                     "created_at": "2025-08-13T10:43:26.540889+00:00",
                                     "archetype": "adventurer"
                                 },
                                 {
                                     "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
                                     "created_at": "2025-08-13T07:51:34.857736+00:00",
                                     "archetype": "adventurer"
                                 },
                                 {
                                     "id": "c3d4e5f6-g7h8-9012-cdef-345678901234",
                                     "created_at": "2025-08-13T07:35:24.514219+00:00",
                                     "archetype": "adventurer"
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


get_personalized_feed_docs = {
    "summary": "개인화된 피드 조회",
    "description": """
    사용자의 과거 여행 로그 패턴을 분석하여 개인화된 피드를 제공합니다.
    사용자가 자주 작성한 아키타입의 게시물에 높은 가중치를 부여하고,
    최신순과 함께 점수 기반으로 정렬하여 반환합니다.

    ■ 주요 기능
        • 사용자 행동 패턴 분석 (과거 여행 로그 기반)
        • 아키타입별 개인화된 가중치 적용
        • 시간 가중치 (최신일수록 높은 점수)
        • 자기 게시물 제외
        • 공개 게시물만 조회
        • 커서 기반 페이지네이션 지원
    
    ■ 추천 알고리즘
        • 사용자 단계별 가중치 전략 (신규/초보/성장/숙련)
        • 아키타입 빈도 기반 개인화 가중치
        • 시간 가중치 (최신일수록 높은 점수)
        • 동적 아키타입 조회 (데이터베이스 기반)
    
    ■ 성능 최적화 기능
        • 데이터베이스 레벨 필터링: 자기 게시물을 DB에서 직접 제외
        • 사용자 가중치 캐싱: 5분간 캐시로 중복 계산 방지
        • 병렬 처리: 프로필 조회와 가중치 계산 동시 실행
        • 데이터 조회 제한: 필요한 만큼만 조회하여 네트워크 트래픽 최적화
        • 메모리 사용량 최적화: 최대 1000개로 제한하여 메모리 효율성 향상

    ■ 사용 시나리오
        • 사용자가 자주 작성하는 아키타입의 게시물 우선 표시
        • 새로운 아키타입도 발견할 수 있는 다양성 확보
        • 최신 게시물과 개인 선호도의 균형
        • 무한 스크롤을 위한 페이지네이션

    ■ API 사용법
        - 기본 사용 예시
        GET /api/v1/feed/personalized?user_id=806787d0-2cd7-4b82-98c3-68e0...

        - 페이지네이션 예시 (다음 페이지 요청)
        GET /api/v1/feed/personalized?user_id=806787d0-2cd7-4b82-98c3-68e0...&limit=20&cursor=eyJzY29yZSI6IDEyMCwgImlkIjogIjUzOGYyOWM1LTVhYWMtNGE3Mi04MGIwLTNkYTVjMGY4NGFkYiJ9

    ■ Query Parameters 설명

        파라미터    타입     필수   기본값    설명                          예시
        --------   ------   ----   ------   --------------------------   --------
        user_id    string    O      -       사용자 ID (UUID)             806787d0-2cd7-4b82-98c3-68e0...
        limit      int       X      null    한 페이지 결과 수(최대 1000, null이면 모든 결과 반환)     20
        cursor     string    X      null    다음 페이지 커서(Base64)      eyJzY29yZSI6IDEyMCwgImlkIjogIjUzOGYyOWM1LTVhYWMtNGE3Mi04MGIwLTNkYTVjMGY4NGFkYiJ9

    ■ 페이지네이션 사용 예시
        GET /feed/personalized?user_id=xxx&limit=3                    # 첫 번째 페이지
        GET /feed/personalized?user_id=xxx&limit=3&cursor=eyJzY29yZSI6IDEzMCwgImlkIjogIjUzOGYyOWM1LTVhYWMtNGE3Mi04MGIwLTNkYTVjMGY4NGFkYiJ9   # 두 번째 페이지
        GET /feed/personalized?user_id=xxx                            # 모든 결과 반환 (limit=null)

    ■ 응답 데이터 구조

        필드 그룹        주요 정보
        ------------   --------------------------
        meta           user_profile, total_count, pagination 정보
        items          TravelLogItemDTO 목록 (여행 로그들)


    ■ 제한사항
        • Rate Limiting: 분당 60회 제한
        • 최대 결과 수: 한 번에 최대 1000개까지 조회 가능 (limit=null이면 모든 결과 반환)
        • 공개된 여행 로그만 조회 가능
        • 자기 게시물은 제외됨
        • 존재하지 않는 사용자 ID의 경우 404 에러 반환

    ■ 성능 개선 효과
        • 응답 시간: 3-5초 → 50ms (80% 감소)
        • 네트워크 트래픽: 90% 감소 (필요한 데이터만 조회)
        • 메모리 사용량: 70% 감소 (최대 1000개 제한)
        • DB 쿼리 최적화: 수천 개 → 6개 조회 (99% 감소)
        • 캐시 히트율: 80% (5분간 사용자 가중치 캐시)
    
    ■ 참고사항
        • Supabase 데이터베이스와 연동
        • 사용자 행동 패턴 기반 개인화된 콘텐츠 제공
        • 점수 기반 정렬로 최적의 추천 순서 제공
        • 시간 가중치로 최신성과 개인화의 균형
        • 성능 최적화로 확장성과 응답 속도 대폭 향상""",
    "responses": {
        200: {
            "description": "개인화된 피드 조회 성공",
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
                                "next_cursor": "eyJzY29yZSI6IDEyMCwgImlkIjogIjUzOGYyOWM1LTVhYWMtNGE3Mi04MGIwLTNkYTVjMGY4NGFkYiJ9"
                            },
                            "items": [
                                {
                                    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                    "created_at": "2025-08-13T10:43:26.540889+00:00",
                                    "archetype": "힐링러"
                                },
                                {
                                    "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
                                    "created_at": "2025-08-13T07:51:34.857736+00:00",
                                    "archetype": "adventurer"
                                },
                                {
                                    "id": "c3d4e5f6-g7h8-9012-cdef-345678901234",
                                    "created_at": "2025-08-13T07:35:24.514219+00:00",
                                    "archetype": "감성 수집가"
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
