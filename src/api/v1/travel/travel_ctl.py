"""
Travel Controller Module

GPS 기반 주변 관광지 목록 조회 API 엔드포인트
"""

from fastapi import APIRouter, Query
from typing import Optional
from src.api.v1.travel import travel_svc
from src.api.v1.travel.travel_dto import (
    TravelListRequestDTO, TravelListResponseDTO,
    TravelCategoryEnum, SortTypeEnum
)
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.travel import travel_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

router = APIRouter(
    prefix="/travel",
    tags=["Travel"],
    responses=Status.docs(ERR.BAD_REQUEST, ERR.TOO_MANY_REQUESTS, ERR.INTERNAL_ERROR)
)


@router.get(
    "/attractions",
    response_model=APIResponse,
    **travel_docs.get_attractions_docs
)
async def get_nearby_attractions(
    lat: float = Query(..., ge=33.0, le=39.0, description="사용자 위치의 위도"),
    lng: float = Query(..., ge=124.0, le=132.0, description="사용자 위치의 경도"),
    radius: int = Query(default=2, ge=1, le=20, description="검색 반경 (km)"),
    category: TravelCategoryEnum = Query(default=TravelCategoryEnum.ALL, description="관광지 유형"),
    sort: SortTypeEnum = Query(default=SortTypeEnum.DISTANCE, description="정렬 방식"),
    limit: int = Query(default=20, ge=1, le=50, description="반환할 최대 결과 수"),
    offset: int = Query(default=0, ge=0, description="결과 시작 위치")
):
    """
    사용자의 GPS 위치를 기반으로 주변 관광지 목록을 조회합니다.
    """
    try:
        # 요청 DTO 생성
        request_dto = TravelListRequestDTO(
            lat=lat,
            lng=lng,
            radius=radius,
            category=category,
            sort=sort,
            limit=limit,
            offset=offset
        )
        
        # 서비스 호출
        result = await travel_svc.travel_service.get_nearby_attractions(request_dto)
        
        # 성공 응답
        return SUC.OK.to_response(detail=result.model_dump())
        
    except ValueError as e:
        # 유효성 검증 오류
        _logger.error(f"Validation error: {str(e)}")
        raise ERR.BAD_REQUEST.to_exception({"error": str(e)})
    except Exception as e:
        # 예상치 못한 오류
        _logger.error(f"Unexpected error in get_nearby_attractions: {str(e)}")
        raise ERR.INTERNAL_ERROR.to_exception()