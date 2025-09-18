"""
Attractions Data Mapper Module

TourAPI 응답 데이터를 내부 DTO로 변환하는 매퍼 함수들
- TourAPI JSON → AttractionsDTO 변환
- 거리 계산 및 포맷팅
- 타입 매핑 및 데이터 정제
"""
from typing import List, Dict, Optional, Tuple
from src.api.v1.travel.attractions_dto import (
    AttractionItemDTO, TourApiItemDTO, CoordinatesDTO
)
from src.api.v1.travel import attractions_utils
from src.core.logger import get_logger

_logger = get_logger(__name__)


def convert_tourapi_to_travel_items(
    api_items: List[Dict], 
    user_lat: float, 
    user_lng: float, 
    source: str = "tourapi"
) -> List[AttractionItemDTO]:
    """
    TourAPI 응답을 TravelItemDTO 리스트로 변환합니다.
    """
    items = []
    
    for api_item in api_items:
        try:
            # TourApiItemDTO로 파싱
            parsed_item = TourApiItemDTO(**api_item)
            
            # 거리 계산
            if parsed_item.mapy and parsed_item.mapx:
                distance_m = attractions_utils.calculate_distance(
                    user_lat, user_lng,
                    float(parsed_item.mapy), float(parsed_item.mapx)
                )
            else:
                distance_m = int(float(parsed_item.dist)) if parsed_item.dist else 0
            
            # 거리 텍스트 생성
            distance_text = attractions_utils.format_distance(distance_m)
            
            # 주소 조합
            address = parsed_item.addr1 or ""
            if parsed_item.addr2:
                address += f" {parsed_item.addr2}"
            
            # 카테고리 타입 및 이름 매핑
            content_type_id = parsed_item.contenttypeid
            type_code, type_name = attractions_utils.get_type_info(content_type_id)
            
            # 위경도 정보 생성
            coordinates = None
            if parsed_item.mapy and parsed_item.mapx:
                try:
                    coordinates = CoordinatesDTO(
                        lat=float(parsed_item.mapy),
                        lng=float(parsed_item.mapx)
                    )
                except (ValueError, TypeError):
                    _logger.warning(f"Invalid coordinates for {parsed_item.title}: lat={parsed_item.mapy}, lng={parsed_item.mapx}")
            
            # AttractionItemDTO 생성
            item = AttractionItemDTO(
                id=parsed_item.contentid,
                type=type_code,
                type_name=type_name,
                name=parsed_item.title,
                thumbnail=parsed_item.firstimage,
                address=address.strip(),
                coordinates=coordinates,
                distance_m=distance_m,
                distance_text=distance_text,
                rating=attractions_utils.get_mock_rating(),
                is_open=True
            )
            
            items.append(item)
            
        except Exception as e:
            _logger.warning(f"Failed to convert travel item: {str(e)}")
            continue
    
    return items
