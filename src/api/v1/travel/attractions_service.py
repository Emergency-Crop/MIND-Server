"""
Attractions Service Module (Middleware)

관광지 API의 미들웨어 역할을 담당하는 서비스
- TourAPI 호출 및 데이터 변환 조율
- 비즈니스 로직 처리 (정렬, 페이지네이션, 거리 계산)
- 에러 처리 및 로깅
- Controller와 외부 API 간의 중간 계층
"""

import httpx
from typing import List, Dict, Tuple
from src.api.v1.travel.attractions_dto import (
    AttractionsRequestDTO, AttractionsResponseDTO, AttractionsDataDTO,
    MetaDTO, PaginationDTO, SearchLocationDTO, AttractionItemDTO,
    AttractionsCategoryEnum, AttractionsSortEnum,
    CATEGORY_NAME_MAPPING, SORT_NAME_MAPPING
)
from src.api.v1.travel.attractions_tourapi import attractions_tourapi
from src.api.v1.travel.attractions_mapper import convert_tourapi_to_travel_items
from src.core.logger import get_logger
from src.config.status import ERR

_logger = get_logger(__name__)


class AttractionsService:
    """관광지 조회 미들웨어 서비스"""
    
    def __init__(self):
        pass
    
    async def get_nearby_attractions(self, request_dto: AttractionsRequestDTO) -> AttractionsResponseDTO:
        """
        GPS 위치 기반으로 주변 관광지 목록을 조회합니다.
        
        Args:
            request_dto: 요청 DTO
            
        Returns:
            AttractionsResponseDTO: 응답 DTO
            
        Raises:
            HTTPException: API 호출 실패 시
        """
        try:
            # 1. TourAPI 호출
            tour_api_items = await self._fetch_from_tour_api(request_dto)
            
            # 2. 응답 데이터 변환
            attraction_items = self._convert_to_attraction_items(tour_api_items, request_dto.lat, request_dto.lng)
            
            # 3. 정렬 적용
            sorted_items = self._apply_sorting(attraction_items, request_dto.sort)
            
            # 4. 페이지네이션 적용
            paginated_items, pagination = self._apply_pagination(
                sorted_items, request_dto.limit, request_dto.offset
            )
            
            # 5. 응답 DTO 생성
            response_data = AttractionsDataDTO(
                meta=MetaDTO(
                    search_location=SearchLocationDTO(
                        lat=request_dto.lat,
                        lng=request_dto.lng
                    ),
                    radius_km=request_dto.radius,
                    category=CATEGORY_NAME_MAPPING[request_dto.category],
                    sort=SORT_NAME_MAPPING[request_dto.sort],
                    pagination=pagination
                ),
                items=paginated_items
            )
            
            return AttractionsResponseDTO(data=response_data)
            
        except httpx.TimeoutException:
            _logger.error("TourAPI timeout occurred")
            raise ERR.GATEWAY_TIMEOUT.to_exception(detail="외부 API 응답 시간 초과")
        except httpx.HTTPError as e:
            _logger.error(f"TourAPI HTTP error: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(detail="외부 API 연동 오류")
        except Exception as e:
            _logger.error(f"Unexpected error in attractions service: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="서버 내부 오류")
    
    async def _fetch_from_tour_api(self, request_dto: AttractionsRequestDTO) -> List[Dict]:
        """
        TourAPI를 호출하여 데이터를 가져옵니다. (미들웨어 역할)
        
        Args:
            request_dto: 요청 DTO
            
        Returns:
            List[Dict]: TourAPI 응답 아이템 목록
        """
        _logger.info(f"TourAPI 호출: lat={request_dto.lat}, lng={request_dto.lng}, radius={request_dto.radius}km")
        
        # TourAPI 모듈을 통해 데이터 조회
        result = await attractions_tourapi.fetch_location_based_list(
            lat=request_dto.lat,
            lng=request_dto.lng,
            radius=request_dto.radius,
            category=request_dto.category,
            sort=request_dto.sort,
            limit=100,  # 내부 정렬/페이징을 위해 더 많은 데이터 조회
            offset=0
        )
        
        return result.get("items", [])
    
    def _convert_to_attraction_items(self, tour_api_items: List[Dict], user_lat: float, user_lng: float) -> List[AttractionItemDTO]:
        """
        TourAPI 응답을 AttractionItemDTO 리스트로 변환합니다. (미들웨어 역할)
        
        Args:
            tour_api_items: TourAPI 응답 아이템 목록
            user_lat: 사용자 위도
            user_lng: 사용자 경도
            
        Returns:
            List[AttractionItemDTO]: 변환된 관광지 아이템 목록
        """
        # 매퍼를 통해 데이터 변환
        return convert_tourapi_to_travel_items(
            tour_api_items, user_lat, user_lng, source="tourapi"
        )
    
    
    def _apply_sorting(self, items: List[AttractionItemDTO], sort_type: AttractionsSortEnum) -> List[AttractionItemDTO]:
        """
        정렬을 적용합니다.
        
        Args:
            items: 정렬할 아이템 목록
            sort_type: 정렬 방식
            
        Returns:
            List[AttractionItemDTO]: 정렬된 아이템 목록
        """
        if sort_type == AttractionsSortEnum.DISTANCE:
            return sorted(items, key=lambda x: x.distance_m)
        elif sort_type == AttractionsSortEnum.NAME:
            return sorted(items, key=lambda x: x.name)
        elif sort_type == AttractionsSortEnum.RATING:
            return sorted(items, key=lambda x: x.rating or 0, reverse=True)
        
        return items
    
    def _apply_pagination(
        self, items: List[AttractionItemDTO], limit: int, offset: int
    ) -> Tuple[List[AttractionItemDTO], PaginationDTO]:
        """
        페이지네이션을 적용합니다.
        
        Args:
            items: 페이지네이션을 적용할 아이템 목록
            limit: 페이지당 아이템 수
            offset: 시작 오프셋
            
        Returns:
            Tuple[List[AttractionItemDTO], PaginationDTO]: (페이지네이션된 아이템, 페이지네이션 정보)
        """
        total_count = len(items)
        
        # 페이지네이션 적용
        start = offset
        end = offset + limit
        paginated_items = items[start:end]
        
        # 페이지네이션 정보 생성
        current_count = len(paginated_items)
        has_more = end < total_count
        next_offset = end if has_more else None
        
        pagination = PaginationDTO(
            total_count=total_count,
            current_count=current_count,
            limit=limit,
            offset=offset,
            has_more=has_more,
            next_offset=next_offset
        )
        
        return paginated_items, pagination


# 서비스 인스턴스 생성
attractions_service = AttractionsService()
