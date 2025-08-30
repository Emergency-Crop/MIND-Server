"""
Feed Controller Module

사용자 아키타입 기반 피드 조회 API 엔드포인트
"""

from fastapi import APIRouter, Query
from typing import Optional
from uuid import UUID
from src.api.v1.feed import feed_svc
from src.api.v1.feed.feed_dto import FeedRequestDTO
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.feed import feed_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
    responses=Status.docs(ERR.BAD_REQUEST, ERR.TOO_MANY_REQUESTS, ERR.INTERNAL_ERROR)
)


@router.get(
    "/test-connection",
    response_model=APIResponse
)
async def test_supabase_connection():
    """
    Supabase 연결 상태를 테스트합니다.
    """
    try:
        result = await feed_svc.feed_service.test_supabase_connection()
        return SUC.OK.to_response(detail=result)
    except Exception as e:
        _logger.error(f"Supabase connection test failed: {str(e)}")
        raise ERR.BAD_GATEWAY.to_exception(detail={"error": str(e)})


@router.get(
    "",
    response_model=APIResponse,
    **feed_docs.get_feed_docs
)
async def get_feed(
    user_id: UUID = Query(..., description="사용자 ID (UUID)"),
    limit: int = Query(default=20, ge=1, le=50, description="반환할 최대 결과 수"),
    cursor: Optional[str] = Query(None, description="다음 페이지 커서 (Base64 인코딩)")
):
    """
    사용자 ID를 기반으로 해당 사용자의 아키타입을 조회하고, 
    같은 아키타입을 가진 다른 사용자들의 여행 로그를 피드로 제공합니다.
    """
    try:
        # 요청 DTO 생성
        request_dto = FeedRequestDTO(
            user_id=user_id,
            limit=limit,
            cursor=cursor
        )
        
        # 서비스 호출
        result = await feed_svc.feed_service.get_feed(request_dto)
        
        # 성공 응답
        return SUC.OK.to_response(detail=result.model_dump())
        
    except ValueError as e:
        # 유효성 검증 오류
        _logger.error(f"Feed validation error: {str(e)}")
        raise ERR.BAD_REQUEST.to_exception({"error": str(e)})
    except Exception as e:
        # NOT_FOUND 에러는 그대로 전달
        if hasattr(e, 'status_code') and e.status_code == 404:
            raise e
        
        # 예상치 못한 오류
        _logger.error(f"Unexpected error in get_feed: {str(e)}")
        raise ERR.INTERNAL_ERROR.to_exception()
