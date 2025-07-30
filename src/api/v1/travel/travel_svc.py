"""
Travel Service Module

한국관광공사 API와 연동하여 관광지 데이터를 조회하는 비즈니스 로직
"""

import httpx
import math
import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode
from src.api.v1.travel.travel_dto import (
    TravelListRequestDTO, TravelListResponseDTO, TravelItemDTO,
    MetaDTO, PaginationDTO, SearchLocationDTO, TravelApiItemDTO,
    TravelCategoryEnum, SortTypeEnum, TravelDetailResponseDTO,
    CoordinatesDTO, ParkingDTO, FacilitiesDTO, NearbyAttractionDTO,
    TransportationDTO, TravelApiDetailDTO, WeatherResponseDTO,
    WeatherLocationDTO, WeatherCurrentDTO,
)
from src.core.env import env
from src.core.logger import get_logger
from src.config.status import ERR
import asyncio
import random

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

# 날씨 상태 코드 매핑
WEATHER_CONDITION_MAPPING = {
    "0": {"condition": "맑음", "condition_code": "clear", "icon": "☀️"},
    "1": {"condition": "구름조금", "condition_code": "partly_cloudy", "icon": "⛅"},
    "3": {"condition": "흐림", "condition_code": "cloudy", "icon": "☁️"},
    "4": {"condition": "흐림", "condition_code": "cloudy", "icon": "☁️"},
    "5": {"condition": "비", "condition_code": "rain", "icon": "🌧️"},
    "6": {"condition": "비/눈", "condition_code": "rain_snow", "icon": "🌨️"},
    "7": {"condition": "눈", "condition_code": "snow", "icon": "❄️"}
}

# 풍향 방위 매핑
WIND_DIRECTION_MAPPING = {
    (0, 22.5): "북풍",
    (22.5, 67.5): "북동풍",
    (67.5, 112.5): "동풍",
    (112.5, 157.5): "남동풍",
    (157.5, 202.5): "남풍",
    (202.5, 247.5): "남서풍",
    (247.5, 292.5): "서풍",
    (292.5, 337.5): "북서풍",
    (337.5, 360): "북풍"
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

    async def get_attraction_detail(self, content_id: str) -> TravelDetailResponseDTO:
        """
        특정 관광지의 상세 정보를 조회합니다.
        """
        try:
            # 1단계: 기본 상세 정보 조회
            detail_data = await self._fetch_detail_from_travel_api(content_id)
            
            if detail_data:
                # 상세 정보가 있으면 상세 정보로 구성
                detail_response = self._convert_to_travel_detail(detail_data)
                # 추가 정보 보충
                await self._enhance_detail_with_additional_apis(detail_response, content_id)
            else:
                # 2단계: 대안 방법으로 정보 수집
                detail_response = await self._fetch_attraction_info_alternative_methods(content_id)
            
            # 주변 관광지 정보 추가 (병렬 처리)
            try:
                nearby_attractions = await self._get_nearby_attractions_for_detail(
                    detail_response.coordinates.lat, 
                    detail_response.coordinates.lng
                )
                detail_response.nearby_attractions = nearby_attractions
            except Exception as e:
                _logger.warning(f"Failed to get nearby attractions: {str(e)}")
                detail_response.nearby_attractions = []
            
            return detail_response
            
        except httpx.TimeoutException:
            _logger.error("Travel API timeout occurred")
            raise ERR.GATEWAY_TIMEOUT.to_exception(detail="외부 API 응답 시간 초과")
        except httpx.HTTPError as e:
            _logger.error(f"Travel API HTTP error: {str(e)}")
            raise ERR.BAD_GATEWAY.to_exception(detail="외부 API 연동 오류")
        except Exception as e:
            # NOT_FOUND 에러는 그대로 전달
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise e
            
            _logger.error(f"Unexpected error in travel detail service: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="서버 내부 오류")

    async def _enhance_detail_with_additional_apis(self, detail_response: TravelDetailResponseDTO, content_id: str):
        """
        추가 API를 사용해서 상세 정보를 보충합니다.
        """
        try:
            # 병렬로 여러 API 호출
            tasks = [
                self._fetch_detail_intro(content_id),
                self._fetch_detail_images(content_id),
                self._fetch_detail_info(content_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            intro_data, images_data, info_data = results
            
            # 소개 정보 보충
            if isinstance(intro_data, dict):
                self._enhance_with_intro_data(detail_response, intro_data)
            
            # 이미지 정보 보충
            if isinstance(images_data, list) and images_data:
                self._enhance_with_images_data(detail_response, images_data)
            
            # 상세 정보 보충
            if isinstance(info_data, dict):
                self._enhance_with_info_data(detail_response, info_data)
                
        except Exception as e:
            _logger.warning(f"Failed to enhance detail with additional APIs: {str(e)}")

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

    async def _fetch_detail_from_travel_api(self, content_id: str) -> Optional[Dict]:
        """
        한국관광공사 API를 호출하여 관광지 상세 정보를 가져옵니다.
        """
        endpoint = f"{self.base_url}/detailCommon2"
        
        # API 파라미터 구성
        params = {
            "serviceKey": self.service_key,
            "numOfRows": "1",
            "pageNo": "1",
            "MobileOS": "WEB",
            "MobileApp": "TravelApp",
            "_type": "json",
            "contentId": content_id,
            "defaultYN": "Y",  # 기본 정보
            "firstImageYN": "Y",  # 대표 이미지
            "areacodeYN": "Y",  # 지역 코드
            "catcodeYN": "Y",  # 카테고리 코드
            "addrinfoYN": "Y",  # 주소 정보
            "mapinfoYN": "Y",  # 지도 정보
            "overviewYN": "Y"  # 개요 정보
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # 전체 응답 로깅 (디버깅용)
            _logger.info(f"Travel API detail raw response for contentId {content_id}: {data}")
            
            # API 응답 검증 - 더 상세한 로깅 추가
            header = data.get("response", {}).get("header", {})
            result_code = header.get("resultCode")
            result_msg = header.get("resultMsg", "Unknown error")
            
            _logger.info(f"Travel API detail response - contentId: {content_id}, resultCode: {result_code}, resultMsg: {result_msg}")
            
            if result_code != "0000":
                _logger.error(f"Travel API detail error for contentId {content_id}: {result_msg}")
                return None
            
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            
            # 단일 아이템인 경우 리스트로 변환
            if isinstance(items, dict):
                items = [items]
            
            if not items:
                _logger.warning(f"No items found for contentId: {content_id}")
                return None
            
            _logger.info(f"Successfully fetched detail for contentId: {content_id}")
            return items[0]

    async def _fetch_basic_info_from_travel_api(self, content_id: str) -> Optional[Dict]:
        """
        한국관광공사 API를 호출하여 관광지 기본 정보를 가져옵니다.
        """
        # 여러 지역에서 검색을 시도
        search_locations = [
            {"lat": 37.5665, "lng": 126.9780, "name": "서울시청"},  # 서울
            {"lat": 35.1796, "lng": 129.0756, "name": "부산"},      # 부산
            {"lat": 35.8714, "lng": 128.6014, "name": "대구"},      # 대구
            {"lat": 37.4563, "lng": 126.7052, "name": "인천"},      # 인천
            {"lat": 35.1595, "lng": 126.8526, "name": "광주"},      # 광주
            {"lat": 36.3504, "lng": 127.3845, "name": "대전"},      # 대전
            {"lat": 37.2911, "lng": 127.0089, "name": "수원"},      # 수원
        ]
        
        for location in search_locations:
            try:
                endpoint = f"{self.base_url}/locationBasedList2"
                
                # API 파라미터 구성
                params = {
                    "serviceKey": self.service_key,
                    "numOfRows": "100",
                    "pageNo": "1",
                    "MobileOS": "WEB",
                    "MobileApp": "TravelApp",
                    "_type": "json",
                    "mapX": str(location["lng"]),
                    "mapY": str(location["lat"]),
                    "radius": "20000",  # 20km 반경
                    "arrange": "E"
                }
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(endpoint, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # API 응답 검증
                    if data.get("response", {}).get("header", {}).get("resultCode") != "0000":
                        continue
                    
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    
                    # 단일 아이템인 경우 리스트로 변환
                    if isinstance(items, dict):
                        items = [items]
                    
                    # contentId로 필터링
                    for item in items:
                        if item.get("contentid") == content_id:
                            _logger.info(f"Found attraction {content_id} in {location['name']}")
                            return item
                            
            except Exception as e:
                _logger.warning(f"Failed to search in {location['name']}: {str(e)}")
                continue
        
        _logger.warning(f"Attraction {content_id} not found in any location")
        return None

    async def _get_nearby_attractions_for_detail(self, lat: float, lng: float) -> List[NearbyAttractionDTO]:
        """
        상세 조회 관광지 주변의 다른 관광지들을 조회합니다.
        """
        try:
            # 주변 관광지 조회를 위한 DTO 생성
            request_dto = TravelListRequestDTO(
                lat=lat,
                lng=lng,
                radius=2,  # 2km 반경
                limit=5,   # 최대 5개
                offset=0
            )
            
            # 주변 관광지 조회
            api_items = await self._fetch_from_travel_api(request_dto)
            
            # NearbyAttractionDTO로 변환
            nearby_attractions = []
            for api_item in api_items:
                try:
                    parsed_item = TravelApiItemDTO(**api_item)
                    
                    # 거리 계산
                    if parsed_item.mapy and parsed_item.mapx:
                        distance_m = self._calculate_distance(
                            lat, lng,
                            float(parsed_item.mapy), float(parsed_item.mapx)
                        )
                    else:
                        distance_m = int(float(parsed_item.dist)) if parsed_item.dist else 0
                    
                    # 거리 텍스트 생성
                    distance_text = self._format_distance(distance_m)
                    
                    nearby_attraction = NearbyAttractionDTO(
                        id=parsed_item.contentid,
                        name=parsed_item.title,
                        distance_m=distance_m,
                        distance_text=distance_text
                    )
                    
                    nearby_attractions.append(nearby_attraction)
                    
                except Exception as e:
                    _logger.warning(f"Failed to convert nearby attraction: {str(e)}")
                    continue
            
            return nearby_attractions
            
        except Exception as e:
            _logger.error(f"Failed to get nearby attractions: {str(e)}")
            return []
    
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

    def _convert_to_travel_item(self, api_item: Dict) -> TravelItemDTO:
        """
        API 응답을 TravelItemDTO로 변환합니다.
        """
        try:
            # 기본 정보 추출
            content_id = api_item.get("contentid", "")
            title = api_item.get("title", "")
            first_image = api_item.get("firstimage", "")
            addr1 = api_item.get("addr1", "")
            addr2 = api_item.get("addr2", "")
            content_type_id = api_item.get("contenttypeid", "")
            
            # 거리 계산 (API에서 제공하는 dist 사용)
            dist = api_item.get("dist", "0")
            try:
                distance_m = int(float(dist))
            except (ValueError, TypeError):
                distance_m = 0
            
            # 거리 텍스트 생성
            distance_text = self._format_distance(distance_m)
            
            # 주소 조합
            address = addr1 or ""
            if addr2:
                address += f" {addr2}"
            
            # 카테고리 타입 및 이름 매핑
            type_code, type_name = self._get_type_info(content_type_id)
            
            # TravelItemDTO 생성
            item = TravelItemDTO(
                id=content_id,
                type=type_code,
                type_name=type_name,
                name=title,
                thumbnail=first_image,
                address=address.strip(),
                distance_m=distance_m,
                distance_text=distance_text,
                rating=self._get_mock_rating(),
                is_open=True
            )
            
            return item
            
        except Exception as e:
            _logger.warning(f"Failed to convert travel item: {str(e)}")
            # 기본값으로 반환
            return TravelItemDTO(
                id=api_item.get("contentid", ""),
                type="unknown",
                type_name="기타",
                name=api_item.get("title", ""),
                thumbnail=api_item.get("firstimage", ""),
                address=api_item.get("addr1", ""),
                distance_m=0,
                distance_text="0m",
                rating=0.0,
                is_open=True
            )

    def _convert_to_travel_detail(self, api_detail: Dict) -> TravelDetailResponseDTO:
        """
        API 상세 응답을 TravelDetailResponseDTO로 변환합니다.
        """
        try:
            # TravelApiDetailDTO로 파싱
            parsed_detail = TravelApiDetailDTO(**api_detail)
            
            # 카테고리 타입 및 이름 매핑
            content_type_id = parsed_detail.contenttypeid
            type_code, type_name = self._get_type_info(content_type_id)
            
            # 주소 조합
            address = parsed_detail.addr1 or ""
            if parsed_detail.addr2:
                address += f" {parsed_detail.addr2}"
            
            # 좌표 변환
            coordinates = None
            if parsed_detail.mapy and parsed_detail.mapx:
                coordinates = CoordinatesDTO(
                    lat=float(parsed_detail.mapy),
                    lng=float(parsed_detail.mapx)
                )
            
            # 이미지 목록 생성
            images = []
            if parsed_detail.firstimage:
                images.append(parsed_detail.firstimage)
            if parsed_detail.firstimage2:
                images.append(parsed_detail.firstimage2)
            
            # 기본 이미지가 없으면 기본 이미지 추가
            if not images:
                images.append("https://via.placeholder.com/400x300?text=No+Image")
            
            # 주차 정보 파싱
            parking = self._parse_parking_info(parsed_detail.parking, parsed_detail.parkingfee)
            
            # 편의시설 정보 파싱
            facilities = self._parse_facilities_info(parsed_detail)
            
            # 태그 생성
            tags = self._generate_tags(parsed_detail, type_code)
            
            # 방문 팁 생성
            tips = self._generate_tips(parsed_detail, type_code)
            
            # 교통 정보 생성
            transportation = self._generate_transportation_info(parsed_detail)
            
            # TravelDetailResponseDTO 생성
            detail_response = TravelDetailResponseDTO(
                id=parsed_detail.contentid,
                name=parsed_detail.title,
                type=type_code,
                type_name=type_name,
                summary=self._generate_summary(parsed_detail.overview),
                description=parsed_detail.overview or "상세 정보가 없습니다.",
                main_image=images[0],
                images=images,
                address=address.strip(),
                coordinates=coordinates or CoordinatesDTO(lat=0.0, lng=0.0),
                phone=parsed_detail.tel,
                website=parsed_detail.homepage,
                rating=self._get_mock_rating(),
                is_open=self._check_is_open(parsed_detail),
                opening_hours=parsed_detail.usetime,
                closed_days=parsed_detail.restdate,
                admission_fee=parsed_detail.admissionfee or "정보 없음",
                parking=parking,
                facilities=facilities,
                tags=tags,
                tips=tips,
                transportation=transportation
            )
            
            return detail_response
            
        except Exception as e:
            _logger.error(f"Failed to convert travel detail: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="데이터 변환 중 오류가 발생했습니다.")

    def _convert_basic_to_detail(self, basic_info: Dict) -> TravelDetailResponseDTO:
        """
        기본 정보를 상세 정보 형태로 변환합니다.
        """
        try:
            # TravelApiItemDTO로 파싱
            parsed_item = TravelApiItemDTO(**basic_info)
            
            # 카테고리 타입 및 이름 매핑
            content_type_id = parsed_item.contenttypeid
            type_code, type_name = self._get_type_info(content_type_id)
            
            # 주소 조합
            address = parsed_item.addr1 or ""
            if parsed_item.addr2:
                address += f" {parsed_item.addr2}"
            
            # 좌표 변환
            coordinates = None
            if parsed_item.mapy and parsed_item.mapx:
                coordinates = CoordinatesDTO(
                    lat=float(parsed_item.mapy),
                    lng=float(parsed_item.mapx)
                )
            
            # 이미지 목록 생성
            images = []
            if parsed_item.firstimage:
                images.append(parsed_item.firstimage)
            
            # 기본 이미지가 없으면 기본 이미지 추가
            if not images:
                images.append("https://via.placeholder.com/400x300?text=No+Image")
            
            # TravelDetailResponseDTO 생성
            detail_response = TravelDetailResponseDTO(
                id=parsed_item.contentid,
                name=parsed_item.title,
                type=type_code,
                type_name=type_name,
                summary=f"{parsed_item.title}에 대한 상세 정보입니다.",
                description=f"{parsed_item.title}에 대한 상세 정보가 제공되지 않습니다. 방문 전 전화로 문의하시기 바랍니다.",
                main_image=images[0],
                images=images,
                address=address.strip(),
                coordinates=coordinates or CoordinatesDTO(lat=0.0, lng=0.0),
                phone=parsed_item.tel,
                website=None,
                rating=self._get_mock_rating(),
                is_open=True,
                opening_hours="정보 없음",
                closed_days="정보 없음",
                admission_fee="정보 없음",
                parking=None,
                facilities=None,
                tags=[type_name, "관광지"],
                tips=["방문 전 전화로 문의하시기 바랍니다."],
                transportation=None
            )
            
            return detail_response
            
        except Exception as e:
            _logger.error(f"Failed to convert basic info to detail: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="데이터 변환 중 오류가 발생했습니다.")

    def _parse_parking_info(self, parking_info: Optional[str], parking_fee: Optional[str]) -> Optional[ParkingDTO]:
        """주차 정보를 파싱합니다."""
        if not parking_info and not parking_fee:
            return None
        
        available = True
        fee = "정보 없음"
        info = parking_info or ""
        
        if parking_fee:
            fee = parking_fee
        
        return ParkingDTO(
            available=available,
            fee=fee,
            info=info
        )

    def _parse_facilities_info(self, detail: TravelApiDetailDTO) -> Optional[FacilitiesDTO]:
        """편의시설 정보를 파싱합니다."""
        return FacilitiesDTO(
            wheelchair_accessible=None,  # API에서 제공하지 않음
            stroller_friendly=detail.chkbabycarriage == "Y" if detail.chkbabycarriage else None,
            pet_allowed=detail.chkpet == "Y" if detail.chkpet else None,
            wifi=None,  # API에서 제공하지 않음
            restaurant=None,  # API에서 제공하지 않음
            gift_shop=None  # API에서 제공하지 않음
        )

    def _generate_tags(self, detail: TravelApiDetailDTO, type_code: str) -> List[str]:
        """관광지 특성 태그를 생성합니다."""
        tags = []
        
        # 타입별 기본 태그
        type_tags = {
            "tourist": ["관광지", "명소"],
            "culture": ["문화시설", "문화"],
            "festival": ["축제", "행사"],
            "course": ["여행코스", "투어"],
            "leisure": ["레포츠", "스포츠"],
            "accommodation": ["숙박", "호텔"],
            "shopping": ["쇼핑", "상점"],
            "restaurant": ["음식점", "맛집"]
        }
        
        tags.extend(type_tags.get(type_code, ["관광지"]))
        
        # 추가 특성 태그
        if detail.scale:
            tags.append("대규모" if "대" in detail.scale else "소규모")
        
        if detail.accomcount:
            tags.append("단체관람")
        
        if detail.chkcreditcard == "Y":
            tags.append("카드결제")
        
        return tags

    def _generate_tips(self, detail: TravelApiDetailDTO, type_code: str) -> List[str]:
        """방문 팁을 생성합니다."""
        tips = []
        
        # 기본 팁
        if detail.spendtime:
            tips.append(f"관람 소요시간: {detail.spendtime}")
        
        if detail.usefee:
            tips.append(f"이용요금: {detail.usefee}")
        
        if detail.discountinfo:
            tips.append(f"할인정보: {detail.discountinfo}")
        
        # 타입별 특화 팁
        if type_code == "tourist":
            tips.append("사진 촬영이 가능한 구역을 미리 확인하세요")
        elif type_code == "restaurant":
            tips.append("혼잡 시간대를 피해서 방문하시는 것을 권장합니다")
        elif type_code == "culture":
            tips.append("전시 관람 시 사진 촬영이 제한될 수 있습니다")
        
        return tips[:5]  # 최대 5개

    def _generate_transportation_info(self, detail: TravelApiDetailDTO) -> Optional[TransportationDTO]:
        """교통 정보를 생성합니다."""
        # 실제 서비스에서는 교통 API를 연동하여 정확한 정보를 제공해야 함
        return TransportationDTO(
            subway=None,
            bus=None,
            parking_info=detail.parking
        )

    def _generate_summary(self, overview: Optional[str]) -> str:
        """개요에서 한 줄 요약을 생성합니다."""
        if not overview:
            return "상세 정보가 없습니다."
        
        # 첫 번째 문장을 요약으로 사용
        summary = overview.split('.')[0]
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        return summary

    def _check_is_open(self, detail: TravelApiDetailDTO) -> bool:
        """현재 운영 상태를 확인합니다."""
        # 실제 서비스에서는 운영시간 정보를 분석하여 정확한 상태를 판단해야 함
        return True
    
    async def _get_recommended_attraction(self) -> TravelDetailResponseDTO:
        """
        기본 추천 관광지를 제공합니다.
        """
        try:
            # 서울의 대표 관광지 중 하나를 반환
            recommended_ids = ["130183", "126508", "126507", "126506"]  # 서울도서관, 경복궁, 창덕궁, 창경궁
            
            for content_id in recommended_ids:
                try:
                    return await self.get_attraction_detail(content_id)
                except Exception:
                    continue
            
            # 모든 추천 관광지가 실패하면 최소한의 정보 제공
            return self._create_minimal_detail_response("130183")
            
        except Exception as e:
            _logger.error(f"Failed to get recommended attraction: {str(e)}")
            return self._create_minimal_detail_response("130183")

    def _get_type_info(self, content_type_id: str) -> Tuple[str, str]:
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

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> int:
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

    def _format_distance(self, distance_m: int) -> str:
        """
        거리를 사람이 읽기 쉬운 형태로 포맷합니다.
        """
        if distance_m < 1000:
            return f"{distance_m}m"
        else:
            km = distance_m / 1000
            return f"{km:.1f}km"

    def _get_mock_rating(self) -> float:
        """
        임시 평점을 생성합니다. 실제 서비스에서는 DB나 별도 API에서 가져와야 합니다.
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

    def _create_minimal_detail_response(self, content_id: str) -> TravelDetailResponseDTO:
        """
        최소한의 정보로 상세 응답을 생성합니다.
        """
        return TravelDetailResponseDTO(
            id=content_id,
            name=f"관광지 (ID: {content_id})",
            type="unknown",
            type_name="기타",
            summary="상세 정보가 제공되지 않는 관광지입니다.",
            description="이 관광지에 대한 상세 정보가 현재 제공되지 않습니다. 방문 전 전화로 문의하시기 바랍니다.",
            main_image="https://via.placeholder.com/400x300?text=No+Image",
            images=["https://via.placeholder.com/400x300?text=No+Image"],
            address="주소 정보 없음",
            coordinates=CoordinatesDTO(lat=0.0, lng=0.0),
            phone=None,
            website=None,
            rating=None,
            is_open=True,
            opening_hours="정보 없음",
            closed_days="정보 없음",
            admission_fee="정보 없음",
            parking=None,
            facilities=None,
            tags=["관광지", "정보제한"],
            tips=["방문 전 전화로 문의하시기 바랍니다.", "상세 정보가 제한적으로 제공됩니다."],
            nearby_attractions=[],
            transportation=None
        )

    async def _fetch_detail_intro(self, content_id: str) -> Optional[Dict]:
        """
        관광지 소개 정보를 가져옵니다.
        """
        # 여러 contentTypeId를 시도
        content_type_ids = ["12", "14", "15", "25", "28", "32", "38", "39"]
        
        for content_type_id in content_type_ids:
            try:
                endpoint = f"{self.base_url}/detailIntro2"
                params = {
                    "serviceKey": self.service_key,
                    "numOfRows": "1",
                    "pageNo": "1",
                    "MobileOS": "WEB",
                    "MobileApp": "TravelApp",
                    "_type": "json",
                    "contentId": content_id,
                    "contentTypeId": content_type_id
                }
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(endpoint, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get("response", {}).get("header", {}).get("resultCode") == "0000":
                        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                        if isinstance(items, dict):
                            items = [items]
                        if items:
                            _logger.info(f"Found intro data for contentId {content_id} with contentTypeId {content_type_id}")
                            return items[0]
                            
            except Exception as e:
                continue
                
        _logger.warning(f"No intro data found for contentId {content_id}")
        return None

    async def _fetch_detail_images(self, content_id: str) -> Optional[List[Dict]]:
        """
        관광지 이미지 정보를 가져옵니다.
        """
        try:
            endpoint = f"{self.base_url}/detailImage2"
            params = {
                "serviceKey": self.service_key,
                "numOfRows": "10",
                "pageNo": "1",
                "MobileOS": "WEB",
                "MobileApp": "TravelApp",
                "_type": "json",
                "contentId": content_id,
                "imageYN": "Y",
                "subImageYN": "Y"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("response", {}).get("header", {}).get("resultCode") == "0000":
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if isinstance(items, dict):
                        items = [items]
                    return items if items else None
                    
        except Exception as e:
            _logger.warning(f"Failed to fetch detail images for {content_id}: {str(e)}")
            return None

    async def _fetch_detail_info(self, content_id: str) -> Optional[Dict]:
        """
        관광지 상세 정보를 가져옵니다.
        """
        # 여러 contentTypeId를 시도
        content_type_ids = ["12", "14", "15", "25", "28", "32", "38", "39"]
        
        for content_type_id in content_type_ids:
            try:
                endpoint = f"{self.base_url}/detailInfo2"
                params = {
                    "serviceKey": self.service_key,
                    "numOfRows": "1",
                    "pageNo": "1",
                    "MobileOS": "WEB",
                    "MobileApp": "TravelApp",
                    "_type": "json",
                    "contentId": content_id,
                    "contentTypeId": content_type_id
                }
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(endpoint, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get("response", {}).get("header", {}).get("resultCode") == "0000":
                        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                        if isinstance(items, dict):
                            items = [items]
                        if items:
                            _logger.info(f"Found info data for contentId {content_id} with contentTypeId {content_type_id}")
                            return items[0]
                            
            except Exception as e:
                continue
                
        _logger.warning(f"No info data found for contentId {content_id}")
        return None

    async def _fetch_attraction_info_alternative_methods(self, content_id: str) -> TravelDetailResponseDTO:
        """
        대안 방법들을 사용해서 관광지 정보를 수집합니다.
        """
        try:
            # 2-1단계: 키워드 검색으로 정보 찾기
            keyword_result = await self._search_by_keyword_alternative(content_id)
            if keyword_result:
                _logger.info(f"Found attraction info via keyword search for contentId {content_id}")
                return keyword_result
            
            # 2-2단계: 위치 기반 검색으로 정보 찾기
            location_result = await self._search_by_location_alternative(content_id)
            if location_result:
                _logger.info(f"Found attraction info via location search for contentId {content_id}")
                return location_result
            
            # 2-3단계: 지역 기반 검색으로 정보 찾기
            area_result = await self._search_by_area_alternative(content_id)
            if area_result:
                _logger.info(f"Found attraction info via area search for contentId {content_id}")
                return area_result
            
            # 2-4단계: 최소한의 정보라도 제공
            _logger.warning(f"No attraction info found via any method for contentId {content_id}")
            return self._create_minimal_detail_response(content_id)
            
        except Exception as e:
            _logger.error(f"Failed to fetch attraction info via alternative methods: {str(e)}")
            return self._create_minimal_detail_response(content_id)

    async def _search_by_keyword_alternative(self, content_id: str) -> Optional[TravelDetailResponseDTO]:
        """
        키워드 검색을 통해 관광지 정보를 찾습니다.
        """
        try:
            # 먼저 기본 정보에서 이름을 가져오기 위해 locationBasedList2 사용
            basic_info = await self._fetch_basic_info_from_travel_api(content_id)
            if not basic_info:
                return None
            
            attraction_name = basic_info.get("title", "")
            if not attraction_name:
                return None
            
            # 키워드 검색으로 더 많은 정보 찾기
            search_result = await self._fetch_search_keyword(attraction_name)
            if search_result:
                # 검색 결과에서 해당 content_id와 일치하는 항목 찾기
                for item in search_result:
                    if item.get("contentid") == content_id:
                        return self._convert_basic_to_detail(item)
            
            # 키워드 검색 결과가 없으면 기본 정보 사용
            return self._convert_basic_to_detail(basic_info)
            
        except Exception as e:
            _logger.warning(f"Failed to search by keyword for {content_id}: {str(e)}")
            return None

    async def _search_by_location_alternative(self, content_id: str) -> Optional[TravelDetailResponseDTO]:
        """
        위치 기반 검색을 통해 관광지 정보를 찾습니다.
        """
        try:
            # 전국 주요 도시에서 위치 기반 검색
            search_locations = [
                {"lat": 37.5665, "lng": 126.9780, "name": "서울"},
                {"lat": 35.1796, "lng": 129.0756, "name": "부산"},
                {"lat": 35.8714, "lng": 128.6014, "name": "대구"},
                {"lat": 37.4563, "lng": 126.7052, "name": "인천"},
                {"lat": 35.1595, "lng": 126.8526, "name": "광주"},
                {"lat": 36.3504, "lng": 127.3845, "name": "대전"},
                {"lat": 37.2911, "lng": 127.0089, "name": "수원"}
            ]
            
            for location in search_locations:
                try:
                    location_result = await self._fetch_location_based_search(
                        location["lat"], location["lng"], content_id
                    )
                    if location_result:
                        _logger.info(f"Found attraction in {location['name']}")
                        return self._convert_basic_to_detail(location_result)
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            _logger.warning(f"Failed to search by location for {content_id}: {str(e)}")
            return None

    async def _search_by_area_alternative(self, content_id: str) -> Optional[TravelDetailResponseDTO]:
        """
        지역 기반 검색을 통해 관광지 정보를 찾습니다.
        """
        try:
            # 주요 지역 코드로 검색
            area_codes = ["1", "2", "3", "4", "5", "6", "7", "8", "31", "32", "33", "34", "35", "36", "37", "38", "39"]
            
            for area_code in area_codes:
                try:
                    area_result = await self._fetch_area_based_search(area_code, content_id)
                    if area_result:
                        _logger.info(f"Found attraction in area {area_code}")
                        return self._convert_basic_to_detail(area_result)
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            _logger.warning(f"Failed to search by area for {content_id}: {str(e)}")
            return None

    async def _fetch_search_keyword(self, keyword: str) -> Optional[List[Dict]]:
        """
        키워드 검색을 수행합니다.
        """
        try:
            endpoint = f"{self.base_url}/searchKeyword2"
            params = {
                "serviceKey": self.service_key,
                "numOfRows": "20",
                "pageNo": "1",
                "MobileOS": "WEB",
                "MobileApp": "TravelApp",
                "_type": "json",
                "keyword": keyword,
                "listYN": "Y",
                "arrange": "A"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("response", {}).get("header", {}).get("resultCode") == "0000":
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if isinstance(items, dict):
                        items = [items]
                    return items if items else None
                    
        except Exception as e:
            _logger.warning(f"Failed to fetch search keyword for {keyword}: {str(e)}")
            return None

    async def _fetch_location_based_search(self, lat: float, lng: float, target_content_id: str) -> Optional[Dict]:
        """
        위치 기반 검색을 수행합니다.
        """
        try:
            endpoint = f"{self.base_url}/locationBasedList2"
            params = {
                "serviceKey": self.service_key,
                "numOfRows": "100",
                "pageNo": "1",
                "MobileOS": "WEB",
                "MobileApp": "TravelApp",
                "_type": "json",
                "mapX": str(lng),
                "mapY": str(lat),
                "radius": "20000",
                "arrange": "A"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("response", {}).get("header", {}).get("resultCode") == "0000":
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if isinstance(items, dict):
                        items = [items]
                    
                    # target_content_id와 일치하는 항목 찾기
                    for item in items:
                        if item.get("contentid") == target_content_id:
                            return item
                    
            return None
                    
        except Exception as e:
            _logger.warning(f"Failed to fetch location based search: {str(e)}")
            return None

    async def _fetch_area_based_search(self, area_code: str, target_content_id: str) -> Optional[Dict]:
        """
        지역 기반 검색을 수행합니다.
        """
        try:
            endpoint = f"{self.base_url}/areaBasedList2"
            params = {
                "serviceKey": self.service_key,
                "numOfRows": "100",
                "pageNo": "1",
                "MobileOS": "WEB",
                "MobileApp": "TravelApp",
                "_type": "json",
                "areaCode": area_code,
                "arrange": "A"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get("response", {}).get("header", {}).get("resultCode") == "0000":
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    if isinstance(items, dict):
                        items = [items]
                    
                    # target_content_id와 일치하는 항목 찾기
                    for item in items:
                        if item.get("contentid") == target_content_id:
                            return item
                    
            return None
                    
        except Exception as e:
            _logger.warning(f"Failed to fetch area based search: {str(e)}")
            return None

    def _enhance_with_intro_data(self, detail_response: TravelDetailResponseDTO, intro_data: Dict):
        """
        소개 정보로 상세 정보를 보충합니다.
        """
        try:
            # 운영시간 정보 보충
            if intro_data.get("usetime") and detail_response.opening_hours == "정보 없음":
                detail_response.opening_hours = intro_data.get("usetime")
            
            # 휴무일 정보 보충
            if intro_data.get("restdate") and detail_response.closed_days == "정보 없음":
                detail_response.closed_days = intro_data.get("restdate")
            
            # 주차 정보 보충
            if intro_data.get("parking") and not detail_response.parking:
                detail_response.parking = ParkingDTO(
                    available=True,
                    fee=intro_data.get("parkingfee", "정보 없음"),
                    info=intro_data.get("parking", "")
                )
            
            # 수용인원 정보 보충
            if intro_data.get("accomcount"):
                detail_response.tips.append(f"수용인원: {intro_data.get('accomcount')}")
                
        except Exception as e:
            _logger.warning(f"Failed to enhance with intro data: {str(e)}")

    def _enhance_with_images_data(self, detail_response: TravelDetailResponseDTO, images_data: List[Dict]):
        """
        이미지 정보로 상세 정보를 보충합니다.
        """
        try:
            # 이미지 URL 추출
            image_urls = []
            for image in images_data:
                if image.get("originimgurl"):
                    image_urls.append(image.get("originimgurl"))
                elif image.get("smallimageurl"):
                    image_urls.append(image.get("smallimageurl"))
            
            # 이미지가 있으면 기존 이미지 대체
            if image_urls:
                detail_response.images = image_urls
                detail_response.main_image = image_urls[0]
                
        except Exception as e:
            _logger.warning(f"Failed to enhance with images data: {str(e)}")

    def _enhance_with_info_data(self, detail_response: TravelDetailResponseDTO, info_data: Dict):
        """
        상세 정보로 상세 정보를 보충합니다.
        """
        try:
            # 이용요금 정보 보충
            if info_data.get("usefee") and detail_response.admission_fee == "정보 없음":
                detail_response.admission_fee = info_data.get("usefee")
            
            # 할인정보 보충
            if info_data.get("discountinfo"):
                detail_response.tips.append(f"할인정보: {info_data.get('discountinfo')}")
            
            # 소요시간 정보 보충
            if info_data.get("spendtime"):
                detail_response.tips.append(f"관람 소요시간: {info_data.get('spendtime')}")
                
        except Exception as e:
            _logger.warning(f"Failed to enhance with info data: {str(e)}")

    async def get_weather(self, lat: float, lng: float) -> WeatherResponseDTO:
        """
        GPS 좌표를 기반으로 현재 날씨 정보를 조회합니다.
        한국관광공사 TourAPI를 통해 기본 날씨 정보를 제공합니다.
        """
        try:
            # 1. 지역명 조회
            area_name = self._get_area_name(lat, lng)
            
            # 2. 기본 날씨 정보 생성 (실제 기상청 API 연동 대신 기본값 제공)
            current_weather = self._generate_basic_weather()
            
            # 3. 여행 적합성 판단 및 조언 생성
            is_travel_friendly, travel_advice = self._judge_travel_friendliness(current_weather)
            
            # 4. 응답 DTO 생성
            location = WeatherLocationDTO(lat=lat, lng=lng, area_name=area_name)
            
            return WeatherResponseDTO(
                location=location,
                current=current_weather,
                updated_at=datetime.datetime.now().isoformat() + "+09:00",
                is_travel_friendly=is_travel_friendly,
                travel_advice=travel_advice
            )
            
        except Exception as e:
            _logger.error(f"Weather API error: {str(e)}")
            raise ERR.INTERNAL_ERROR.to_exception(detail="날씨 정보 조회 중 오류가 발생했습니다")

    def _generate_basic_weather(self) -> WeatherCurrentDTO:
        """
        기본 날씨 정보를 생성합니다.
        실제 서비스에서는 기상청 API를 연동하여 실시간 데이터를 제공해야 합니다.
        """
        # 기본값 생성 (실제로는 기상청 API에서 가져와야 함)
        temperature = random.uniform(15.0, 25.0)
        humidity = random.randint(40, 80)
        precipitation = 0.0
        wind_speed = random.uniform(1.0, 5.0)
        wind_direction = random.randint(0, 360)
        
        # 텍스트 변환
        temperature_text = f"{round(temperature)}°"
        humidity_text = f"{humidity}%"
        precipitation_text = "강수없음"
        wind_text = self._format_wind(wind_direction, wind_speed)
        
        # 날씨 상태 (기본적으로 맑음)
        weather_condition = {"condition": "맑음", "condition_code": "clear", "icon": "☀️"}
        
        return WeatherCurrentDTO(
            temperature=temperature,
            temperature_text=temperature_text,
            humidity=humidity,
            humidity_text=humidity_text,
            precipitation=precipitation,
            precipitation_text=precipitation_text,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            wind_text=wind_text,
            condition=weather_condition["condition"],
            condition_code=weather_condition["condition_code"],
            icon=weather_condition["icon"]
        )

    def _format_wind(self, direction: int, speed: float) -> str:
        """풍향/풍속 텍스트 변환"""
        # 풍향 방위 변환
        wind_direction_text = "북풍"
        for (min_angle, max_angle), direction_name in WIND_DIRECTION_MAPPING.items():
            if min_angle <= direction < max_angle:
                wind_direction_text = direction_name
                break
        
        return f"{wind_direction_text} {speed}m/s"

    def _get_area_name(self, lat: float, lng: float) -> str:
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

    def _judge_travel_friendliness(self, weather: WeatherCurrentDTO) -> Tuple[bool, str]:
        """
        날씨 정보를 기반으로 여행 적합성 판단 및 조언 생성
        """
        # 여행 적합성 판단 기준
        is_good_temp = -10 <= weather.temperature <= 35
        is_good_precipitation = weather.precipitation < 1.0
        is_good_wind = weather.wind_speed < 10.0
        
        is_travel_friendly = is_good_temp and is_good_precipitation and is_good_wind
        
        # 조언 생성
        advice_parts = []
        
        if not is_good_temp:
            if weather.temperature < -10:
                advice_parts.append("날씨가 매우 춥습니다. 따뜻한 옷을 챙기세요.")
            elif weather.temperature > 35:
                advice_parts.append("날씨가 매우 덥습니다. 시원한 곳에서 휴식을 취하세요.")
        
        if not is_good_precipitation:
            advice_parts.append("비가 올 예정입니다. 우산을 챙기세요.")
        
        if not is_good_wind:
            advice_parts.append("바람이 강합니다. 외출 시 주의하세요.")
        
        if is_travel_friendly:
            if weather.temperature < 10:
                advice_parts.append("날씨가 쌀쌀합니다. 겉옷을 챙기세요.")
            elif weather.temperature > 25:
                advice_parts.append("날씨가 따뜻합니다. 가벼운 옷차림이 좋겠습니다.")
            else:
                advice_parts.append("여행하기 좋은 날씨입니다.")
        
        travel_advice = " ".join(advice_parts) if advice_parts else "날씨 정보를 확인하세요."
        
        return is_travel_friendly, travel_advice


# 서비스 인스턴스 생성
travel_service = TravelService()