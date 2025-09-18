"""
Attractions Detail Service Module

관광지 상세 정보 조회 서비스
- TourAPI 상세 정보 조회 (공통정보, 소개정보, 이미지정보)
- 데이터 변환 및 가공
- 주변 관광지 조회
- 에러 처리 및 로깅
"""

import asyncio
import random
import re
from typing import List, Dict, Optional, Tuple
from src.api.v1.travel.attractions_detail_dto import (
    AttractionDetailResponseDTO, AttractionDetailDataDTO,
    CoordinatesDTO, ParkingDTO, FacilitiesDTO, NearbyAttractionDTO, TransportationDTO,
    TourApiDetailCommonDTO, TourApiDetailIntroDTO, TourApiDetailImageDTO,
    TOURAPI_TO_TYPE_MAPPING, DEFAULT_IMAGE_URL, DEFAULT_THUMBNAIL_URL
)
from src.api.v1.travel.attractions_tourapi import attractions_tourapi
from src.api.v1.travel.attractions_utils import calculate_distance, format_distance
from src.core.logger import get_logger
from src.config.status import ERR

_logger = get_logger(__name__)


class AttractionsDetailService:
    """관광지 상세 정보 조회 서비스"""
    
    def __init__(self):
        pass
    
    async def get_attraction_detail(self, content_id: str) -> AttractionDetailResponseDTO:
        """
        관광지 상세 정보를 조회합니다.
        
        Args:
            content_id: 관광지 콘텐츠 ID
            
        Returns:
            AttractionDetailResponseDTO: 상세 정보 응답 DTO
        """
        try:
            
            # 1. TourAPI 병렬 호출
            common_task = attractions_tourapi.fetch_detail_common(content_id)
            intro_task = None  # content_type_id가 필요하므로 나중에 호출
            images_task = attractions_tourapi.fetch_detail_images(content_id)
            
            # 공통정보 먼저 조회
            common_result = await common_task
            if not common_result.get("items"):
                raise ERR.NOT_FOUND.to_exception(
                    detail={"error": "ATTRACTION_NOT_FOUND", "message": "존재하지 않는 관광지입니다."}
                )
            
            common_data = common_result["items"][0]
            content_type_id = common_data.get("contenttypeid", "12")
            
            # 소개정보 조회
            intro_task = attractions_tourapi.fetch_detail_intro(content_id, content_type_id)
            intro_result = await intro_task
            images_result = await images_task
            
            # 2. 데이터 변환
            detail_data = self._convert_to_detail_data(
                common_data, 
                intro_result.get("items", [{}])[0] if intro_result.get("items") else {},
                images_result.get("items", [])
            )
            
            # 3. 주변 관광지 조회 (선택적)
            if detail_data.coordinates:
                nearby_attractions = await self._get_nearby_attractions(
                    detail_data.coordinates.lat, 
                    detail_data.coordinates.lng,
                    content_id
                )
                detail_data.nearby_attractions = nearby_attractions
            
            # 4. 응답 생성
            response = AttractionDetailResponseDTO(
                success=True,
                message="관광지 상세 정보 조회가 완료되었습니다.",
                data=detail_data
            )
            
            return response
            
        except Exception as e:
            _logger.error(f"상세 정보 조회 오류: {str(e)}")
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise e
            raise ERR.INTERNAL_ERROR.to_exception(detail="서버 내부 오류")
    
    def _convert_to_detail_data(
        self, 
        common_data: Dict, 
        intro_data: Dict, 
        images_data: List[Dict]
    ) -> AttractionDetailDataDTO:
        """TourAPI 데이터를 상세 정보 DTO로 변환"""
        
        # 기본 정보
        content_id = common_data.get("contentid", "")
        content_type_id = common_data.get("contenttypeid", "12")
        type_code, type_name = TOURAPI_TO_TYPE_MAPPING.get(content_type_id, ("unknown", "기타"))
        
        # 좌표 정보
        coordinates = None
        if common_data.get("mapy") and common_data.get("mapx"):
            try:
                coordinates = CoordinatesDTO(
                    lat=float(common_data["mapy"]),
                    lng=float(common_data["mapx"])
                )
            except (ValueError, TypeError):
                pass
        
        # 이미지 처리
        main_image = common_data.get("firstimage") or DEFAULT_IMAGE_URL
        images = [main_image]
        
        # 추가 이미지 추가
        for img_data in images_data[:9]:  # 최대 10개 (메인 이미지 포함)
            img_url = img_data.get("originimgurl")
            if img_url and img_url not in images:
                images.append(img_url)
        
        # 주소 조합
        address = common_data.get("addr1", "")
        if common_data.get("addr2"):
            address += f" {common_data['addr2']}"
        
        # 개요 정보 처리
        overview = common_data.get("overview", "")
        summary = self._extract_summary(overview)
        description = self._clean_html(overview) if overview else "상세 정보가 없습니다."
        
        # 편의시설 정보 추출
        facilities = self._extract_facilities(intro_data, content_type_id)
        
        # 주차 정보 추출
        parking = self._extract_parking_info(intro_data, content_type_id)
        
        # 운영 정보 추출
        opening_hours, closed_days, admission_fee = self._extract_operating_info(intro_data, content_type_id)
        
        # 태그 생성
        tags = self._generate_tags(type_name, common_data, intro_data)
        
        # 방문 팁 생성
        tips = self._generate_tips(type_name, intro_data)
        
        # 교통 정보 생성
        transportation = self._generate_transportation_info(common_data, intro_data)
        
        return AttractionDetailDataDTO(
            id=content_id,
            name=common_data.get("title", "알 수 없는 관광지"),
            type=type_code,
            type_name=type_name,
            summary=summary,
            description=description,
            main_image=main_image,
            images=images,
            address=address.strip(),
            coordinates=coordinates,
            phone=common_data.get("tel"),
            website=common_data.get("homepage"),
            rating=self._get_mock_rating(),
            is_open=True,  # 실제 서비스에서는 운영시간 확인 필요
            opening_hours=opening_hours,
            closed_days=closed_days,
            admission_fee=admission_fee,
            parking=parking,
            facilities=facilities,
            tags=tags,
            tips=tips,
            nearby_attractions=None,  # 나중에 설정
            transportation=transportation
        )
    
    def _extract_summary(self, overview: str) -> str:
        """개요에서 한 줄 요약 추출"""
        if not overview:
            return "상세 정보가 없습니다."
        
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', overview)
        # 첫 번째 문장 추출 (100자 이내)
        sentences = clean_text.split('.')
        first_sentence = sentences[0].strip()
        
        if len(first_sentence) > 100:
            return first_sentence[:97] + "..."
        return first_sentence
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거 및 텍스트 정리"""
        if not text:
            return ""
        
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 연속된 공백 제거
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    
    def _extract_facilities(self, intro_data: Dict, content_type_id: str) -> Optional[FacilitiesDTO]:
        """편의시설 정보 추출"""
        facilities = {}
        
        if content_type_id == "12":  # 관광지
            facilities.update({
                "wheelchair_accessible": self._parse_yes_no(intro_data.get("chkbabycarriage")),
                "stroller_friendly": self._parse_yes_no(intro_data.get("chkbabycarriage")),
                "pet_allowed": self._parse_yes_no(intro_data.get("chkpet")),
                "wifi": self._parse_yes_no(intro_data.get("chkcreditcard")),
                "restaurant": "식당" in (intro_data.get("infocenter") or ""),
                "gift_shop": "기념품" in (intro_data.get("infocenter") or "")
            })
        elif content_type_id == "14":  # 문화시설
            facilities.update({
                "wheelchair_accessible": self._parse_yes_no(intro_data.get("chkbabycarriageculture")),
                "stroller_friendly": self._parse_yes_no(intro_data.get("chkbabycarriageculture")),
                "pet_allowed": self._parse_yes_no(intro_data.get("chkpetculture")),
                "wifi": self._parse_yes_no(intro_data.get("chkcreditcardculture")),
                "restaurant": "식당" in (intro_data.get("infocenterculture") or ""),
                "gift_shop": "기념품" in (intro_data.get("infocenterculture") or "")
            })
        
        # 모든 값이 None이면 None 반환
        if not any(facilities.values()):
            return None
            
        return FacilitiesDTO(**facilities)
    
    def _extract_parking_info(self, intro_data: Dict, content_type_id: str) -> Optional[ParkingDTO]:
        """주차 정보 추출"""
        parking_info = None
        
        if content_type_id == "12":  # 관광지
            parking_info = intro_data.get("parking")
        elif content_type_id == "14":  # 문화시설
            parking_info = intro_data.get("parkingculture")
        elif content_type_id == "32":  # 숙박
            parking_info = intro_data.get("parkinglodging")
        elif content_type_id == "38":  # 쇼핑
            parking_info = intro_data.get("parkingshopping")
        elif content_type_id == "39":  # 음식점
            parking_info = intro_data.get("parkingfood")
        
        if not parking_info or parking_info == "없음":
            return ParkingDTO(available=False)
        
        return ParkingDTO(
            available=True,
            fee=self._extract_parking_fee(parking_info),
            info=parking_info
        )
    
    def _extract_operating_info(self, intro_data: Dict, content_type_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """운영 정보 추출"""
        opening_hours = None
        closed_days = None
        admission_fee = None
        
        if content_type_id == "12":  # 관광지
            opening_hours = intro_data.get("usetime")
            closed_days = intro_data.get("restdate")
            admission_fee = intro_data.get("usefee") or "무료"
        elif content_type_id == "14":  # 문화시설
            opening_hours = intro_data.get("usetimeculture")
            closed_days = intro_data.get("restdateculture")
            admission_fee = intro_data.get("usefee")
        elif content_type_id == "38":  # 쇼핑
            opening_hours = intro_data.get("opentime")
            closed_days = intro_data.get("restdateshopping")
        elif content_type_id == "39":  # 음식점
            opening_hours = intro_data.get("opentimefood")
            closed_days = intro_data.get("restdatefood")
        
        return opening_hours, closed_days, admission_fee
    
    def _generate_tags(self, type_name: str, common_data: Dict, intro_data: Dict) -> List[str]:
        """태그 생성"""
        tags = [type_name]
        
        # 카테고리 기반 태그
        cat1 = common_data.get("cat1", "")
        if cat1:
            cat_mapping = {
                "A01": "자연", "A02": "인문", "A03": "레저", "A04": "쇼핑", "A05": "음식"
            }
            if cat1 in cat_mapping:
                tags.append(cat_mapping[cat1])
        
        # 특성 기반 태그
        if intro_data.get("heritage1") == "1":
            tags.append("세계문화유산")
        if intro_data.get("heritage2") == "1":
            tags.append("세계자연유산")
        if intro_data.get("heritage3") == "1":
            tags.append("세계기록유산")
        
        # 주차 가능 여부
        parking_info = intro_data.get("parking") or intro_data.get("parkingculture")
        if parking_info and "가능" in parking_info:
            tags.append("주차가능")
        
        # 무료 여부
        usefee = intro_data.get("usefee") or intro_data.get("usefeeleports")
        if usefee and "무료" in usefee:
            tags.append("무료")
        
        return list(set(tags))  # 중복 제거
    
    def _generate_tips(self, type_name: str, intro_data: Dict) -> List[str]:
        """방문 팁 생성"""
        tips = []
        
        # 운영시간 팁
        usetime = intro_data.get("usetime") or intro_data.get("usetimeculture")
        if usetime and "상시" not in usetime:
            tips.append(f"운영시간: {usetime}")
        
        # 휴무일 팁
        restdate = intro_data.get("restdate") or intro_data.get("restdateculture")
        if restdate and "무휴" not in restdate:
            tips.append(f"휴무일: {restdate}")
        
        # 입장료 팁
        usefee = intro_data.get("usefee") or intro_data.get("usefeeleports")
        if usefee and "무료" not in usefee:
            tips.append(f"입장료: {usefee}")
        
        # 주차 팁
        parking = intro_data.get("parking") or intro_data.get("parkingculture")
        if parking and "가능" in parking:
            tips.append("주차장 이용 가능")
        
        return tips[:5]  # 최대 5개
    
    def _generate_transportation_info(self, common_data: Dict, intro_data: Dict) -> Optional[TransportationDTO]:
        """교통 정보 생성"""
        subway_info = []
        bus_info = []
        
        # 주소에서 지하철역 추출 (간단한 예시)
        address = common_data.get("addr1", "")
        if "서울" in address:
            subway_info.append("서울 지하철 이용 가능")
        elif "부산" in address:
            subway_info.append("부산 지하철 이용 가능")
        
        # 주차 정보
        parking_info = intro_data.get("parking") or intro_data.get("parkingculture")
        if parking_info:
            parking_info = f"주차: {parking_info}"
        else:
            parking_info = "주차 정보 없음"
        
        if not subway_info and not bus_info:
            return None
            
        return TransportationDTO(
            subway=subway_info if subway_info else None,
            bus=bus_info if bus_info else None,
            parking_info=parking_info
        )
    
    async def _get_nearby_attractions(self, lat: float, lng: float, exclude_id: str) -> List[NearbyAttractionDTO]:
        """주변 관광지 조회"""
        try:
            # 주변 관광지 조회 (반경 2km)
            result = await attractions_tourapi.fetch_location_based_list(
                lat=lat, lng=lng, radius=2, category="all", sort="distance", limit=5, offset=0
            )
            
            nearby_attractions = []
            for item in result.get("items", []):
                if item.get("contentid") == exclude_id:
                    continue
                
                # 거리 계산
                if item.get("mapy") and item.get("mapx"):
                    distance_m = calculate_distance(
                        lat, lng, 
                        float(item["mapy"]), float(item["mapx"])
                    )
                else:
                    distance_m = int(float(item.get("dist", 0)))
                
                nearby_attractions.append(NearbyAttractionDTO(
                    id=item.get("contentid", ""),
                    name=item.get("title", ""),
                    distance_m=distance_m,
                    distance_text=format_distance(distance_m)
                ))
            
            return nearby_attractions[:5]  # 최대 5개
            
        except Exception as e:
            _logger.warning(f"주변 관광지 조회 실패: {str(e)}")
            return []
    
    def _parse_yes_no(self, value: str) -> Optional[bool]:
        """예/아니오 문자열을 boolean으로 변환"""
        if not value:
            return None
        return "가능" in value or "있음" in value or "예" in value
    
    def _extract_parking_fee(self, parking_info: str) -> Optional[str]:
        """주차 요금 정보 추출"""
        if not parking_info:
            return None
        
        # 요금 정보가 포함된 경우 추출
        if "요금" in parking_info:
            return parking_info
        elif "무료" in parking_info:
            return "무료"
        else:
            return "유료"
    
    def _get_mock_rating(self) -> float:
        """임시 평점 생성"""
        return round(random.uniform(3.5, 5.0), 1)


# 서비스 인스턴스 생성
attractions_detail_service = AttractionsDetailService()
