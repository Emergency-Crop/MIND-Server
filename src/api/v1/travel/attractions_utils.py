"""
Travel Utilities Module

여행 관련 공통 유틸리티 함수들
"""
import random
from typing import List, Tuple
from src.api.v1.travel.attractions_dto import AttractionItemDTO, AttractionsSortEnum
from src.api.v1.travel.attractions_dto import PaginationDTO


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    """
    두 지점 간의 거리를 계산합니다 (미터 단위).
    """
    try:
        from math import radians, cos, sin, asin, sqrt
        
        # 위도, 경도를 라디안으로 변환
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Haversine 공식
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # 지구 반지름 (미터)
        
        return int(c * r)
    except Exception:
        return 0


def format_distance(distance_m: int) -> str:
    """
    거리를 사람이 읽기 쉬운 형태로 포맷합니다.
    """
    if distance_m < 1000:
        return f"{distance_m}m"
    else:
        km = distance_m / 1000
        return f"{km:.1f}km"


def get_mock_rating() -> float:
    """
    임시 평점을 생성합니다. 실제 서비스에서는 DB나 별도 API에서 가져와야 합니다.
    """
    return round(random.uniform(3.5, 5.0), 1)


def apply_sorting(items: List[AttractionItemDTO], sort_type: AttractionsSortEnum) -> List[AttractionItemDTO]:
    """
    정렬을 적용합니다.
    """
    if sort_type == AttractionsSortEnum.DISTANCE:
        return sorted(items, key=lambda x: x.distance_m)
    elif sort_type == AttractionsSortEnum.NAME:
        return sorted(items, key=lambda x: x.name)
    elif sort_type == AttractionsSortEnum.RATING:
        return sorted(items, key=lambda x: x.rating or 0, reverse=True)
    
    return items


def apply_pagination(
    items: List[AttractionItemDTO], limit: int, offset: int
) -> Tuple[List[AttractionItemDTO], PaginationDTO]:
    """
    페이지네이션을 적용합니다.
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


def get_type_info(content_type_id: str) -> Tuple[str, str]:
    """
    contentTypeId를 기반으로 타입 정보를 반환합니다.
    """
    type_mapping = {
        "12": ("tourist_spot", "관광지"),
        "14": ("cultural_facility", "문화시설"),
        "15": ("festival_event", "축제/행사"),
        "25": ("course", "여행코스"),
        "28": ("leisure_sports", "레포츠"),
        "32": ("lodging", "숙박"),
        "38": ("shopping", "쇼핑"),
        "39": ("restaurant", "음식점")
    }
    
    return type_mapping.get(content_type_id, ("unknown", "기타"))


def get_area_name(lat: float, lng: float) -> str:
    """
    GPS 좌표를 기반으로 지역명 조회 (간단한 매핑)
    실제 구현에서는 reverse geocoding API 사용 권장
    """
    # 간단한 지역 매핑 (실제로는 더 정확한 reverse geocoding 필요)
    if 37.4 <= lat <= 37.7 and 126.8 <= lng <= 127.2:
        return "서울특별시"
    elif 35.1 <= lat <= 35.2 and 129.0 <= lng <= 129.1:
        return "부산광역시"
    elif 35.8 <= lat <= 35.9 and 128.5 <= lng <= 128.6:
        return "대구광역시"
    elif 37.4 <= lat <= 37.5 and 127.0 <= lng <= 127.1:
        return "경기도"
    else:
        return "한국"

