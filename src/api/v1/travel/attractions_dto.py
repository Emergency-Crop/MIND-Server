"""
Attractions API DTO Module

명세서에 따른 주변 관광지 목록 조회 API의 요청/응답 스키마 정의
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum


class AttractionsCategoryEnum(str, Enum):
    """관광지 카테고리 Enum (클라이언트 요청 기준)"""
    ALL = "all"
    TOURIST = "tourist"          # 관광지 (12)
    CULTURE = "culture"          # 문화시설 (14)
    FESTIVAL = "festival"        # 축제/행사 (15)
    COURSE = "course"            # 여행코스 (25)
    LEISURE = "leisure"          # 레포츠 (28)
    ACCOMMODATION = "accommodation"  # 숙박 (32)
    SHOPPING = "shopping"        # 쇼핑 (38)
    RESTAURANT = "restaurant"    # 음식점 (39)


class AttractionsSortEnum(str, Enum):
    """정렬 방식 Enum"""
    DISTANCE = "distance"  # 거리순
    NAME = "name"          # 제목순
    RATING = "rating"      # 평점순 (내부 데이터 사용)


# ==========================================
# Request DTOs
# ==========================================

class AttractionsRequestDTO(BaseModel):
    """주변 관광지 목록 조회 요청 DTO"""
    lat: float = Field(..., ge=33.0, le=39.0, description="사용자 위치의 위도")
    lng: float = Field(..., ge=124.0, le=132.0, description="사용자 위치의 경도")
    radius: int = Field(2, ge=1, le=20, description="검색 반경 (km 단위, 기본값: 2, 최대: 20)")
    category: AttractionsCategoryEnum = Field(AttractionsCategoryEnum.ALL, description="관광지 유형")
    sort: AttractionsSortEnum = Field(AttractionsSortEnum.DISTANCE, description="정렬 방식")
    limit: int = Field(20, ge=1, le=50, description="반환할 최대 결과 수")
    offset: int = Field(0, ge=0, description="결과 시작 위치")

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


# ==========================================
# Response DTOs
# ==========================================

class SearchLocationDTO(BaseModel):
    """검색 기준 위치 DTO"""
    lat: float = Field(..., description="검색 기준 위도")
    lng: float = Field(..., description="검색 기준 경도")


class PaginationDTO(BaseModel):
    """페이지네이션 정보 DTO"""
    total_count: int = Field(..., description="검색된 총 결과 수")
    current_count: int = Field(..., description="현재 페이지 결과 수")
    limit: int = Field(..., description="요청된 결과 수 제한")
    offset: int = Field(..., description="현재 페이지 시작 위치")
    has_more: bool = Field(..., description="추가 결과 존재 여부")
    next_offset: Optional[int] = Field(None, description="다음 페이지 offset (has_more가 true일 때만)")


class MetaDTO(BaseModel):
    """검색 메타 정보 DTO"""
    search_location: SearchLocationDTO = Field(..., description="검색 기준 위치")
    radius_km: int = Field(..., description="검색 반경 (km)")
    category: str = Field(..., description="검색된 카테고리")
    sort: str = Field(..., description="적용된 정렬 방식")
    pagination: PaginationDTO = Field(..., description="페이지네이션 정보")


class AttractionItemDTO(BaseModel):
    """관광지 항목 DTO"""
    id: str = Field(..., description="관광지 고유 ID (상세 조회용)")
    type: str = Field(..., description="관광지 타입 (영문)")
    type_name: str = Field(..., description="관광지 타입 (한글)")
    name: str = Field(..., description="관광지 명칭")
    thumbnail: Optional[str] = Field(None, description="썸네일 이미지 URL")
    address: str = Field(..., description="주소")
    coordinates: Optional["CoordinatesDTO"] = Field(None, description="GPS 좌표")
    distance_m: int = Field(..., description="거리 (미터)")
    distance_text: str = Field(..., description="거리 (사용자 친화적 텍스트)")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="평점 (1.0-5.0)")
    is_open: Optional[bool] = Field(None, description="현재 운영 상태")


class AttractionsDataDTO(BaseModel):
    """관광지 목록 응답 데이터 DTO"""
    meta: MetaDTO = Field(..., description="검색 메타 정보")
    items: List[AttractionItemDTO] = Field(..., description="관광지 목록")


class AttractionsResponseDTO(BaseModel):
    """관광지 목록 조회 응답 DTO"""
    success: bool = Field(True, description="요청 성공 여부")
    message: str = Field("주변 관광지 조회가 완료되었습니다.", description="응답 메시지")
    data: AttractionsDataDTO = Field(..., description="응답 데이터 객체")


# ==========================================
# TourAPI 관련 DTOs
# ==========================================

class TourApiItemDTO(BaseModel):
    """한국관광공사 API 응답 아이템 DTO"""
    contentid: str = Field(..., description="콘텐츠 ID")
    contenttypeid: str = Field(..., description="콘텐츠 타입 ID")
    title: str = Field(..., description="제목")
    addr1: Optional[str] = Field(None, description="주소1")
    addr2: Optional[str] = Field(None, description="주소2")
    firstimage: Optional[str] = Field(None, description="대표이미지")
    firstimage2: Optional[str] = Field(None, description="대표이미지(썸네일)")
    mapx: Optional[str] = Field(None, description="경도")
    mapy: Optional[str] = Field(None, description="위도")
    dist: Optional[str] = Field(None, description="거리")
    tel: Optional[str] = Field(None, description="전화번호")
    areacode: Optional[str] = Field(None, description="지역코드")
    sigungucode: Optional[str] = Field(None, description="시군구코드")
    cat1: Optional[str] = Field(None, description="대분류")
    cat2: Optional[str] = Field(None, description="중분류")
    cat3: Optional[str] = Field(None, description="소분류")
    createdtime: Optional[str] = Field(None, description="등록일")
    modifiedtime: Optional[str] = Field(None, description="수정일")
    zipcode: Optional[str] = Field(None, description="우편번호")
    mlevel: Optional[str] = Field(None, description="Map Level")
    cpyrhtDivCd: Optional[str] = Field(None, description="저작권 유형")
    
    class Config:
        extra = "ignore"  # 추가 필드 무시


class TourApiResponseDTO(BaseModel):
    """한국관광공사 API 응답 DTO"""
    resultCode: str = Field(..., description="결과 코드")
    resultMsg: str = Field(..., description="결과 메시지")
    numOfRows: int = Field(..., description="한 페이지 결과 수")
    pageNo: int = Field(..., description="페이지 번호")
    totalCount: int = Field(..., description="전체 결과 수")
    items: Optional[List[TourApiItemDTO]] = Field(None, description="아이템 목록")


# ==========================================
# 카테고리 매핑 상수
# ==========================================

# 클라이언트 카테고리 -> TourAPI contenttypeid 매핑
CATEGORY_TO_TOURAPI_MAPPING = {
    AttractionsCategoryEnum.ALL: None,
    AttractionsCategoryEnum.TOURIST: "12",
    AttractionsCategoryEnum.CULTURE: "14",
    AttractionsCategoryEnum.FESTIVAL: "15",
    AttractionsCategoryEnum.COURSE: "25",
    AttractionsCategoryEnum.LEISURE: "28",
    AttractionsCategoryEnum.ACCOMMODATION: "32",
    AttractionsCategoryEnum.SHOPPING: "38",
    AttractionsCategoryEnum.RESTAURANT: "39"
}

# 클라이언트 카테고리 -> 한글명 매핑
CATEGORY_NAME_MAPPING = {
    AttractionsCategoryEnum.ALL: "전체",
    AttractionsCategoryEnum.TOURIST: "관광지",
    AttractionsCategoryEnum.CULTURE: "문화시설",
    AttractionsCategoryEnum.FESTIVAL: "축제/행사",
    AttractionsCategoryEnum.COURSE: "여행코스",
    AttractionsCategoryEnum.LEISURE: "레포츠",
    AttractionsCategoryEnum.ACCOMMODATION: "숙박",
    AttractionsCategoryEnum.SHOPPING: "쇼핑",
    AttractionsCategoryEnum.RESTAURANT: "음식점"
}

# 정렬 방식 -> 한글명 매핑
SORT_NAME_MAPPING = {
    AttractionsSortEnum.DISTANCE: "거리순",
    AttractionsSortEnum.NAME: "제목순",
    AttractionsSortEnum.RATING: "평점순"
}

# 정렬 방식 -> TourAPI arrange 매핑
SORT_TO_TOURAPI_MAPPING = {
    AttractionsSortEnum.DISTANCE: "E",  # 거리순
    AttractionsSortEnum.NAME: "A",      # 제목순
    AttractionsSortEnum.RATING: "E"     # API에서 평점순은 지원하지 않으므로 거리순으로 대체
}

# TourAPI contenttypeid -> 클라이언트 타입 매핑
TOURAPI_TO_TYPE_MAPPING = {
    "12": ("tourist", "관광지"),
    "14": ("culture", "문화시설"),
    "15": ("festival", "축제/행사"),
    "25": ("course", "여행코스"),
    "28": ("leisure", "레포츠"),
    "32": ("accommodation", "숙박"),
    "38": ("shopping", "쇼핑"),
    "39": ("restaurant", "음식점")
}

# ==========================================
# Legacy DTOs (travel_dto.py에서 이동)
# ==========================================

class TravelCategoryEnum(str, Enum):
    """관광지 카테고리 Enum (TourAPI 기준) - Legacy"""
    ALL = "all"
    TOURIST = "tourist"          # 관광지 (12)
    CULTURE = "culture"          # 문화시설 (14)
    FESTIVAL = "festival"        # 축제/행사 (15)
    COURSE = "course"            # 여행코스 (25)
    LEISURE = "leisure"          # 레포츠 (28)
    ACCOMMODATION = "accommodation"  # 숙박 (32)
    SHOPPING = "shopping"        # 쇼핑 (38)
    RESTAURANT = "restaurant"    # 음식점 (39)


class SortTypeEnum(str, Enum):
    """정렬 방식 Enum - Legacy"""
    DISTANCE = "distance"  # 거리순
    NAME = "name"          # 제목순
    RATING = "rating"      # 평점순 (내부 데이터 사용)


class TravelListRequestDTO(BaseModel):
    """주변 관광지 목록 조회 요청 DTO - Legacy"""
    lat: float = Field(..., ge=33.0, le=39.0, description="사용자 위치의 위도 (33.0~39.0)", example=37.5665)
    lng: float = Field(..., ge=124.0, le=132.0, description="사용자 위치의 경도 (124.0~132.0)", example=126.9780)
    radius_m: int = Field(default=2000, ge=100, le=20000, description="검색 반경 (미터, 100~20000)", example=2000)
    radius: Optional[int] = Field(default=None, ge=1, le=20, description="(Deprecated) km 단위 반경. 제공 시 radius_m로 자동 변환", example=2)
    category: "TravelCategoryEnum" = Field(default="all", description="관광지 유형")
    sort: "SortTypeEnum" = Field(default="distance", description="정렬 방식")
    limit: int = Field(default=20, ge=1, le=50, description="반환할 최대 결과 수", example=20)
    offset: int = Field(default=0, ge=0, description="결과 시작 위치", example=0)

    @field_validator("lat")
    def validate_latitude(cls, v: float):
        if not (33.0 <= v <= 39.0):
            raise ValueError("위도는 33.0과 39.0 사이여야 합니다.")
        return v

    @field_validator("lng")
    def validate_longitude(cls, v: float):
        if not (124.0 <= v <= 132.0):
            raise ValueError("경도는 124.0과 132.0 사이여야 합니다.")
        return v

    @field_validator("radius_m", mode="before")
    def apply_radius_legacy(cls, v, info):
        """radius(km)가 들어오면 radius_m로 변환"""
        data = info.data
        radius_km = data.get("radius") if data else None
        if radius_km is not None:
            m = radius_km * 1000
            if m < 100:
                m = 100
            elif m > 20000:
                m = 20000
            return m
        return v


class TravelItemDTO(BaseModel):
    """관광지 항목 (소스 불문 공통 스키마) - Legacy"""
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


class TravelApiItemDTO(BaseModel):
    """TourAPI 파싱용 DTO - Legacy"""
    contentid: str = Field(..., description="관광지 고유 ID")
    contenttypeid: str = Field(..., description="관광지 타입 ID")
    title: str = Field(..., description="관광지 명칭")
    addr1: Optional[str] = Field(None, description="주소1")
    addr2: Optional[str] = Field(None, description="주소2")
    firstimage: Optional[str] = Field(None, description="대표 이미지 URL")
    mapx: Optional[str] = Field(None, description="지도 X 좌표")
    mapy: Optional[str] = Field(None, description="지도 Y 좌표")
    dist: Optional[str] = Field(None, description="거리")
    tel: Optional[str] = Field(None, description="전화번호")

    class Config:
        extra = "ignore"


class CoordinatesDTO(BaseModel):
    """GPS 좌표 DTO"""
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
