"""
Travel DTO Module

GPS 기반 주변 관광지 목록 조회 API의 요청/응답 스키마 정의
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from enum import Enum


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