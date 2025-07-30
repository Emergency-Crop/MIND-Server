"""
Travel Service Module

한국관광공사 API와 연동하여 관광지 데이터를 조회하는 비즈니스 로직
"""

import httpx
import math
from typing import List, Dict, Optional
from urllib.parse import urlencode
from src.api.v1.travel.travel_dto import (
    TravelListRequestDTO, TravelListResponseDTO, TravelItemDTO,
    MetaDTO, PaginationDTO, SearchLocationDTO, TravelApiItemDTO,
    TravelCategoryEnum, SortTypeEnum
)
from src.core.env import env
from src.core.logger import get_logger
from src.config.status import ERR

_logger = get_logger(__name__)

# 카테고리 매핑 테이블
CATEGORY_MAPPING = {
    TravelCategoryEnum.ALL: None,
    TravelCategoryEnum.TOURIST: "12",
    TravelCategoryEnum.CULTURE: "14",
    TravelCategoryEnum.FESTIVAL: "15",
    TravelCategoryEnum.COURSE: "25",
    TravelCategoryEnum.LEISURE: "28",
    TravelCategoryEnum.ACCOMMODATION: "32",
    TravelCategoryEnum.SHOPPING: "38",
    TravelCategoryEnum.RESTAURANT: "39"
}

CATEGORY_NAME_MAPPING = {
    TravelCategoryEnum.ALL: "전체",
    TravelCategoryEnum.TOURIST: "관광지",
    TravelCategoryEnum.CULTURE: "문화시설",
    TravelCategoryEnum.FESTIVAL: "축제/행사",
    TravelCategoryEnum.COURSE: "여행코스",
    TravelCategoryEnum.LEISURE: "레포츠",
    TravelCategoryEnum.ACCOMMODATION: "숙박",
    TravelCategoryEnum.SHOPPING: "쇼핑",
    TravelCategoryEnum.RESTAURANT: "음식점"
}

SORT_NAME_MAPPING = {
    SortTypeEnum.DISTANCE: "거리순",
    SortTypeEnum.NAME: "제목순",
    SortTypeEnum.RATING: "평점순"
}

# 한국관광공사 API 정렬 매핑
TRAVEL_API_SORT_MAPPING = {
    SortTypeEnum.DISTANCE: "E",  # 거리순
    SortTypeEnum.NAME: "A",  # 제목순
    SortTypeEnum.RATING: "E"  # API에서 평점순은 지원하지 않으므로 거리순으로 대체
}


class TravelService:
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/B551011/KorService2"
        self.service_key = env.TOUR_API_KEY  # 환경변수에서 API 키 가져오기
        self.timeout = httpx.Timeout(10.0)
        
    async def get_nearby_attractions(self, dto: TravelListRequestDTO) -> TravelListResponseDTO:
        """
        GPS 위치 기반으로 주변 관광지 목록을 조회합니다.
        """
        try:
            # 한국관광공사 API 호출
            api_items = await self._fetch_from_travel_api(dto)
            
            # 응답 데이터 변환
            items = self._convert_to_travel_items(api_items, dto.lat, dto.lng)
            
            # 정렬 적용
            sorted_items = self._apply_sorting(items, dto.sort)
            
            # 페이지네이션 적용
            paginated_items, pagination = self._apply_pagination(
                sorted_items, dto.limit, dto.offset
            )
            
            # 응답 생성
            return TravelListResponseDTO(
                meta=MetaDTO(
                    search_location=SearchLocationDTO(lat=dto.lat, lng=dto.lng),
                    radius_km=dto.radius,
                    category=CATEGORY_NAME_MAPPING[dto.category],
                    sort=SORT_NAME_MAPPING[dto.sort],
                    pagination=pagination
                ),
                items=paginated_items
            )
            
        except httpx.TimeoutException:
            _logger.error("Travel API timeout occurred")
            raise ERR.GATEWAY_TIMEOUT.to_exception(detail="외부 API 응답 시간 초과")
        except httpx.HTTPError as e:
            _logger.error(f"Travel API HTTP error: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(detail="외부 API 연동 오류")
        except Exception as e:
            _logger.error(f"Unexpected error in travel service: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="서버 내부 오류")
    
    async def _fetch_from_travel_api(self, dto: TravelListRequestDTO) -> List[Dict]:
        """
        한국관광공사 API를 호출하여 데이터를 가져옵니다.
        """
        endpoint = f"{self.base_url}/locationBasedList2"
        
        # API 파라미터 구성
        params = {
            "serviceKey": self.service_key,
            "numOfRows": "100",  # API에서 더 많은 데이터를 가져와서 내부 정렬/페이징
            "pageNo": "1",
            "MobileOS": "WEB",
            "MobileApp": "TravelApp",
            "_type": "json",
            "mapX": str(dto.lng),
            "mapY": str(dto.lat),
            "radius": str(dto.radius * 1000),  # km를 m로 변환
            "arrange": TRAVEL_API_SORT_MAPPING[dto.sort]
        }
        
        # 카테고리 필터 추가
        if dto.category != TravelCategoryEnum.ALL:
            params["contentTypeId"] = CATEGORY_MAPPING[dto.category]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # API 응답 검증
            if data.get("response", {}).get("header", {}).get("resultCode") != "0000":
                error_msg = data.get("response", {}).get("header", {}).get("resultMsg", "Unknown error")
                _logger.error(f"Travel API error: {error_msg}")
                raise ERR.BAD_GATEWAY.to_exception(detail=f"Travel API error: {error_msg}")
            
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            # 단일 아이템인 경우 리스트로 변환
            if isinstance(items, dict):
                items = [items]
            
            return items
    
    def _convert_to_travel_items(self, api_items: List[Dict], user_lat: float, user_lng: float) -> List[TravelItemDTO]:
        """
        API 응답을 TravelItemDTO 리스트로 변환합니다.
        """
        items = []
        
        for api_item in api_items:
            try:
                # TravelApiItemDTO로 파싱
                parsed_item = TravelApiItemDTO(**api_item)
                
                # 거리 계산
                if parsed_item.mapy and parsed_item.mapx:
                    distance_m = self._calculate_distance(
                        user_lat, user_lng,
                        float(parsed_item.mapy), float(parsed_item.mapx)
                    )
                else:
                    distance_m = int(float(parsed_item.dist)) if parsed_item.dist else 0
                
                # 거리 텍스트 생성
                distance_text = self._format_distance(distance_m)
                
                # 주소 조합
                address = parsed_item.addr1 or ""
                if parsed_item.addr2:
                    address += f" {parsed_item.addr2}"
                
                # 카테고리 타입 및 이름 매핑
                content_type_id = parsed_item.contenttypeid
                type_code, type_name = self._get_type_info(content_type_id)
                
                # TravelItemDTO 생성
                item = TravelItemDTO(
                    id=parsed_item.contentid,
                    type=type_code,
                    type_name=type_name,
                    name=parsed_item.title,
                    thumbnail=parsed_item.firstimage,
                    address=address.strip(),
                    distance_m=distance_m,
                    distance_text=distance_text,
                    rating=self._get_mock_rating(),  # 실제 서비스에서는 DB나 별도 API에서 가져와야 함
                    is_open=True  # 실제 서비스에서는 운영시간 정보를 확인해야 함
                )
                
                items.append(item)
                
            except Exception as e:
                _logger.warning(f"Failed to convert travel item: {str(e)}")
                continue
        
        return items
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> int:
        """
        두 지점 사이의 거리를 계산합니다 (Haversine formula).
        결과는 미터 단위로 반환됩니다.
        """
        R = 6371000  # 지구 반지름 (미터)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return int(distance)
    
    def _format_distance(self, distance_m: int) -> str:
        """
        거리를 사용자 친화적인 텍스트로 변환합니다.
        """
        if distance_m < 1000:
            return f"{distance_m}m"
        else:
            km = distance_m / 1000
            return f"{km:.1f}km"
    
    def _get_type_info(self, content_type_id: str) -> tuple[str, str]:
        """
        콘텐츠 타입 ID를 기반으로 타입 코드와 이름을 반환합니다.
        """
        type_mapping = {
            "12": ("tourist", "관광지"),
            "14": ("culture", "문화시설"),
            "15": ("festival", "축제/행사"),
            "25": ("course", "여행코스"),
            "28": ("leisure", "레포츠"),
            "32": ("accommodation", "숙박"),
            "38": ("shopping", "쇼핑"),
            "39": ("restaurant", "음식점")
        }
        
        return type_mapping.get(content_type_id, ("etc", "기타"))
    
    def _get_mock_rating(self) -> float:
        """
        임시 평점을 반환합니다. 실제 서비스에서는 DB나 별도 API에서 가져와야 합니다.
        """
        import random
        return round(random.uniform(3.5, 5.0), 1)
    
    def _apply_sorting(self, items: List[TravelItemDTO], sort_type: SortTypeEnum) -> List[TravelItemDTO]:
        """
        정렬을 적용합니다.
        """
        if sort_type == SortTypeEnum.DISTANCE:
            return sorted(items, key=lambda x: x.distance_m)
        elif sort_type == SortTypeEnum.NAME:
            return sorted(items, key=lambda x: x.name)
        elif sort_type == SortTypeEnum.RATING:
            return sorted(items, key=lambda x: x.rating or 0, reverse=True)
        
        return items
    
    def _apply_pagination(
        self, items: List[TravelItemDTO], limit: int, offset: int
    ) -> tuple[List[TravelItemDTO], PaginationDTO]:
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


# 서비스 인스턴스 생성
travel_service = TravelService()