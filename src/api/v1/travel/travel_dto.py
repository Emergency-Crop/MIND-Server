"""
Travel DTO Module

GPS 기반 주변 관광지 목록 조회 API의 요청/응답 스키마 정의
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from enum import Enum
from datetime import datetime


class TravelCategoryEnum(str, Enum):
    """관광지 카테고리 Enum"""
    ALL = "all"
    TOURIST = "tourist"  # 관광지 (12)
    CULTURE = "culture"  # 문화시설 (14)
    FESTIVAL = "festival"  # 축제/행사 (15)
    COURSE = "course"  # 여행코스 (25)
    LEISURE = "leisure"  # 레포츠 (28)
    ACCOMMODATION = "accommodation"  # 숙박 (32)
    SHOPPING = "shopping"  # 쇼핑 (38)
    RESTAURANT = "restaurant"  # 음식점 (39)


class SortTypeEnum(str, Enum):
    """정렬 방식 Enum"""
    DISTANCE = "distance"  # 거리순
    NAME = "name"  # 제목순
    RATING = "rating"  # 평점순 (내부 데이터 사용)


# Weather API 관련 DTO
class WeatherLocationDTO(BaseModel):
    """날씨 위치 정보 DTO"""
    lat: float = Field(..., description="요청된 위도")
    lng: float = Field(..., description="요청된 경도")
    area_name: Optional[str] = Field(None, description="지역명 (시/도 시/군/구)")


class WeatherCurrentDTO(BaseModel):
    """현재 날씨 정보 DTO"""
    temperature: float = Field(..., description="기온 (섭씨, °C)")
    temperature_text: str = Field(..., description="기온 표시용 텍스트")
    humidity: int = Field(..., description="습도 (%)")
    humidity_text: str = Field(..., description="습도 표시용 텍스트")
    precipitation: float = Field(..., description="1시간 강수량 (mm)")
    precipitation_text: str = Field(..., description="강수 표시용 텍스트")
    wind_speed: float = Field(..., description="풍속 (m/s)")
    wind_direction: int = Field(..., description="풍향 (도, 0-360)")
    wind_text: str = Field(..., description="바람 표시용 텍스트")
    condition: str = Field(..., description="날씨 상태 (한글)")
    condition_code: str = Field(..., description="날씨 상태 코드 (영문)")
    icon: str = Field(..., description="날씨 아이콘 (이모지)")


class WeatherResponseDTO(BaseModel):
    """날씨 조회 응답 DTO"""
    location: WeatherLocationDTO = Field(..., description="위치 정보")
    current: WeatherCurrentDTO = Field(..., description="현재 날씨 정보")
    updated_at: str = Field(..., description="마지막 업데이트 시간 (ISO 8601)")
    is_travel_friendly: bool = Field(..., description="여행 적합 여부")
    travel_advice: str = Field(..., description="여행 관련 조언")


class TravelListRequestDTO(BaseModel):
    """관광지 목록 조회 요청 DTO"""
    lat: float = Field(..., ge=33.0, le=39.0, description="사용자 위치의 위도")
    lng: float = Field(..., ge=124.0, le=132.0, description="사용자 위치의 경도")
    radius: int = Field(default=2, ge=1, le=20, description="검색 반경 (km)")
    category: TravelCategoryEnum = Field(default=TravelCategoryEnum.ALL, description="관광지 유형")
    sort: SortTypeEnum = Field(default=SortTypeEnum.DISTANCE, description="정렬 방식")
    limit: int = Field(default=20, ge=1, le=50, description="반환할 최대 결과 수")
    offset: int = Field(default=0, ge=0, description="결과 시작 위치")

    @field_validator('lat')
    def validate_latitude(cls, v):
        if not (33.0 <= v <= 39.0):
            raise ValueError("위도는 33.0과 39.0 사이의 값이어야 합니다.")
        return v

    @field_validator('lng')
    def validate_longitude(cls, v):
        if not (124.0 <= v <= 132.0):
            raise ValueError("경도는 124.0과 132.0 사이의 값이어야 합니다.")
        return v


class SearchLocationDTO(BaseModel):
    """검색 기준 위치 DTO"""
    lat: float
    lng: float


class PaginationDTO(BaseModel):
    """페이지네이션 정보 DTO"""
    total_count: int
    current_count: int
    limit: int
    offset: int
    has_more: bool
    next_offset: Optional[int] = None


class MetaDTO(BaseModel):
    """검색 메타 정보 DTO"""
    search_location: SearchLocationDTO
    radius_km: int
    category: str
    sort: str
    pagination: PaginationDTO


class TravelItemDTO(BaseModel):
    """관광지 항목 DTO"""
    id: str = Field(..., description="관광지 고유 ID")
    type: str = Field(..., description="관광지 타입 (영문)")
    type_name: str = Field(..., description="관광지 타입 (한글)")
    name: str = Field(..., description="관광지 명칭")
    thumbnail: Optional[str] = Field(None, description="썸네일 이미지 URL")
    address: str = Field(..., description="주소")
    distance_m: int = Field(..., description="거리 (미터)")
    distance_text: str = Field(..., description="거리 (텍스트)")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="평점")
    is_open: Optional[bool] = Field(None, description="현재 운영 상태")


class TravelListResponseDTO(BaseModel):
    """관광지 목록 조회 응답 DTO"""
    meta: MetaDTO
    items: List[TravelItemDTO]


# 상세 조회 관련 DTO
class CoordinatesDTO(BaseModel):
    """GPS 좌표 DTO"""
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")


class ParkingDTO(BaseModel):
    """주차 정보 DTO"""
    available: bool = Field(..., description="주차 가능 여부")
    fee: Optional[str] = Field(None, description="주차 요금 정보")
    info: Optional[str] = Field(None, description="주차 관련 추가 정보")


class FacilitiesDTO(BaseModel):
    """편의시설 정보 DTO"""
    wheelchair_accessible: Optional[bool] = Field(None, description="휠체어 접근 가능")
    stroller_friendly: Optional[bool] = Field(None, description="유모차 이용 가능")
    pet_allowed: Optional[bool] = Field(None, description="반려동물 입장 가능")
    wifi: Optional[bool] = Field(None, description="와이파이 제공")
    restaurant: Optional[bool] = Field(None, description="식당/매점 있음")
    gift_shop: Optional[bool] = Field(None, description="기념품샵 있음")


class NearbyAttractionDTO(BaseModel):
    """주변 관광지 DTO"""
    id: str = Field(..., description="주변 관광지 ID")
    name: str = Field(..., description="주변 관광지 명칭")
    distance_m: int = Field(..., description="거리 (미터)")
    distance_text: str = Field(..., description="거리 (텍스트)")


class TransportationDTO(BaseModel):
    """교통 정보 DTO"""
    subway: Optional[List[str]] = Field(None, description="지하철 정보")
    bus: Optional[List[str]] = Field(None, description="버스 정보")
    parking_info: Optional[str] = Field(None, description="주차 안내")


class TravelDetailResponseDTO(BaseModel):
    """관광지 상세 조회 응답 DTO"""
    # 기본 정보
    id: str = Field(..., description="관광지 고유 ID")
    name: str = Field(..., description="관광지 명칭")
    type: str = Field(..., description="관광지 타입 (영문)")
    type_name: str = Field(..., description="관광지 타입 (한글)")
    summary: str = Field(..., description="한 줄 요약 (리스트뷰용)")
    description: str = Field(..., description="상세 설명")
    
    # 이미지 정보
    main_image: str = Field(..., description="대표 이미지 URL")
    images: List[str] = Field(..., description="이미지 URL 목록")
    
    # 위치 정보
    address: str = Field(..., description="주소")
    coordinates: CoordinatesDTO = Field(..., description="GPS 좌표")
    
    # 연락처 정보
    phone: Optional[str] = Field(None, description="전화번호")
    website: Optional[str] = Field(None, description="공식 웹사이트 URL")
    
    # 운영 정보
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="평점")
    is_open: bool = Field(..., description="현재 운영 상태")
    opening_hours: Optional[str] = Field(None, description="운영 시간")
    closed_days: Optional[str] = Field(None, description="휴무일")
    admission_fee: Optional[str] = Field(None, description="입장료")
    
    # 편의시설
    parking: Optional[ParkingDTO] = Field(None, description="주차 정보")
    facilities: Optional[FacilitiesDTO] = Field(None, description="편의시설 정보")
    
    # 부가 정보
    tags: List[str] = Field(..., description="관광지 특성 태그")
    tips: Optional[List[str]] = Field(None, description="방문 팁")
    nearby_attractions: Optional[List[NearbyAttractionDTO]] = Field(None, description="주변 관광지")
    
    # 교통 정보
    transportation: Optional[TransportationDTO] = Field(None, description="대중교통 정보")


# 한국관광공사 API 응답 파싱용 DTO
class TravelApiItemDTO(BaseModel):
    """한국관광공사 API 응답 아이템 DTO"""
    contentid: str = Field(..., description="콘텐츠 ID")
    contenttypeid: str = Field(..., description="콘텐츠 타입 ID")
    title: str = Field(..., description="제목")
    addr1: Optional[str] = Field(None, description="주소1")
    addr2: Optional[str] = Field(None, description="주소2")
    firstimage: Optional[str] = Field(None, description="대표이미지")
    mapx: Optional[str] = Field(None, description="경도")
    mapy: Optional[str] = Field(None, description="위도")
    dist: Optional[str] = Field(None, description="거리")
    tel: Optional[str] = Field(None, description="전화번호")
    
    class Config:
        extra = "ignore"  # 추가 필드 무시


class TravelApiDetailDTO(BaseModel):
    """한국관광공사 API 상세 정보 응답 DTO"""
    contentid: str = Field(..., description="콘텐츠 ID")
    contenttypeid: str = Field(..., description="콘텐츠 타입 ID")
    title: str = Field(..., description="제목")
    addr1: Optional[str] = Field(None, description="주소1")
    addr2: Optional[str] = Field(None, description="주소2")
    firstimage: Optional[str] = Field(None, description="대표이미지")
    firstimage2: Optional[str] = Field(None, description="대표이미지2")
    mapx: Optional[str] = Field(None, description="경도")
    mapy: Optional[str] = Field(None, description="위도")
    tel: Optional[str] = Field(None, description="전화번호")
    homepage: Optional[str] = Field(None, description="홈페이지")
    overview: Optional[str] = Field(None, description="개요")
    usetime: Optional[str] = Field(None, description="이용시간")
    restdate: Optional[str] = Field(None, description="휴무일")
    parking: Optional[str] = Field(None, description="주차정보")
    admissionfee: Optional[str] = Field(None, description="입장료")
    infocenter: Optional[str] = Field(None, description="문의 및 안내")
    scale: Optional[str] = Field(None, description="규모")
    accomcount: Optional[str] = Field(None, description="수용인원")
    usefee: Optional[str] = Field(None, description="이용요금")
    discountinfo: Optional[str] = Field(None, description="할인정보")
    spendtime: Optional[str] = Field(None, description="소요시간")
    parkingfee: Optional[str] = Field(None, description="주차요금")
    chkbabycarriage: Optional[str] = Field(None, description="유모차 대여")
    chkpet: Optional[str] = Field(None, description="애완동물 동반")
    chkcreditcard: Optional[str] = Field(None, description="신용카드 가능")
    
    class Config:
        extra = "ignore"  # 추가 필드 무시