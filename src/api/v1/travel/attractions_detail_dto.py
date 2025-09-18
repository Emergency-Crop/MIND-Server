"""
Attractions Detail DTO Module

관광지 상세 정보 조회 API의 데이터 전송 객체들
- 상세 정보 요청/응답 DTO
- TourAPI 상세 정보 응답 DTO
- 내부 데이터 변환용 DTO
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class AttractionDetailResponseDTO(BaseModel):
    """관광지 상세 정보 응답 DTO"""
    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: "AttractionDetailDataDTO" = Field(..., description="상세 정보 데이터")


class AttractionDetailDataDTO(BaseModel):
    """관광지 상세 정보 데이터 DTO"""
    # 기본 정보
    id: str = Field(..., description="관광지 고유 ID")
    name: str = Field(..., description="관광지 명칭")
    type: str = Field(..., description="관광지 타입 (영문)")
    type_name: str = Field(..., description="관광지 타입 (한글)")
    summary: str = Field(..., description="한 줄 요약")
    description: str = Field(..., description="상세 설명")
    
    # 이미지 정보
    main_image: str = Field(..., description="대표 이미지 URL")
    images: List[str] = Field(..., description="이미지 URL 목록")
    
    # 위치 정보
    address: str = Field(..., description="주소")
    coordinates: "CoordinatesDTO" = Field(..., description="GPS 좌표")
    
    # 연락처 정보
    phone: Optional[str] = Field(None, description="전화번호")
    website: Optional[str] = Field(None, description="공식 웹사이트 URL")
    
    # 운영 정보
    rating: Optional[float] = Field(None, description="평점 (1.0-5.0)")
    is_open: bool = Field(..., description="현재 운영 상태")
    opening_hours: Optional[str] = Field(None, description="운영 시간")
    closed_days: Optional[str] = Field(None, description="휴무일")
    admission_fee: Optional[str] = Field(None, description="입장료")
    
    # 편의시설
    parking: Optional["ParkingDTO"] = Field(None, description="주차 정보")
    facilities: Optional["FacilitiesDTO"] = Field(None, description="편의시설 정보")
    
    # 부가 정보
    tags: List[str] = Field(..., description="관광지 특성 태그")
    tips: Optional[List[str]] = Field(None, description="방문 팁")
    nearby_attractions: Optional[List["NearbyAttractionDTO"]] = Field(None, description="주변 관광지")
    
    # 교통 정보
    transportation: Optional["TransportationDTO"] = Field(None, description="대중교통 정보")


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
    """대중교통 정보 DTO"""
    subway: Optional[List[str]] = Field(None, description="지하철 정보")
    bus: Optional[List[str]] = Field(None, description="버스 정보")
    parking_info: Optional[str] = Field(None, description="주차 안내")


# TourAPI 상세 정보 응답 DTO들
class TourApiDetailCommonDTO(BaseModel):
    """TourAPI 공통정보 조회 응답 DTO"""
    contentid: str
    contenttypeid: str
    createdtime: str
    homepage: Optional[str] = None
    modifiedtime: str
    tel: Optional[str] = None
    telname: Optional[str] = None
    title: str
    firstimage: Optional[str] = None
    firstimage2: Optional[str] = None
    cpyrhtDivCd: Optional[str] = None
    areacode: Optional[str] = None
    sigungucode: Optional[str] = None
    cat1: Optional[str] = None
    cat2: Optional[str] = None
    cat3: Optional[str] = None
    addr1: Optional[str] = None
    addr2: Optional[str] = None
    zipcode: Optional[str] = None
    mapx: Optional[str] = None
    mapy: Optional[str] = None
    mlevel: Optional[str] = None
    overview: Optional[str] = None
    lDongRegnCd: Optional[str] = None
    lDongSignguCd: Optional[str] = None
    lclsSystm1: Optional[str] = None
    lclsSystm2: Optional[str] = None
    lclsSystm3: Optional[str] = None


class TourApiDetailIntroDTO(BaseModel):
    """TourAPI 소개정보 조회 응답 DTO"""
    contentid: str
    contenttypeid: str
    
    # 관광지 (contentTypeId=12)
    accomcount: Optional[str] = None
    chkbabycarriage: Optional[str] = None
    chkcreditcard: Optional[str] = None
    chkpet: Optional[str] = None
    expagerange: Optional[str] = None
    expguide: Optional[str] = None
    heritage1: Optional[str] = None
    heritage2: Optional[str] = None
    heritage3: Optional[str] = None
    infocenter: Optional[str] = None
    opendate: Optional[str] = None
    parking: Optional[str] = None
    restdate: Optional[str] = None
    useseason: Optional[str] = None
    usetime: Optional[str] = None
    
    # 문화시설 (contentTypeId=14)
    accomcountculture: Optional[str] = None
    chkbabycarriageculture: Optional[str] = None
    chkcreditcardculture: Optional[str] = None
    chkpetculture: Optional[str] = None
    discountinfo: Optional[str] = None
    infocenterculture: Optional[str] = None
    parkingculture: Optional[str] = None
    parkingfee: Optional[str] = None
    restdateculture: Optional[str] = None
    usefee: Optional[str] = None
    usetimeculture: Optional[str] = None
    scale: Optional[str] = None
    spendtime: Optional[str] = None
    
    # 행사/공연/축제 (contentTypeId=15)
    agelimit: Optional[str] = None
    bookingplace: Optional[str] = None
    discountinfofestival: Optional[str] = None
    eventenddate: Optional[str] = None
    eventhomepage: Optional[str] = None
    eventplace: Optional[str] = None
    eventstartdate: Optional[str] = None
    festivalgrade: Optional[str] = None
    placeinfo: Optional[str] = None
    playtime: Optional[str] = None
    program: Optional[str] = None
    spendtimefestival: Optional[str] = None
    sponsor1: Optional[str] = None
    sponsor1tel: Optional[str] = None
    sponsor2: Optional[str] = None
    sponsor2tel: Optional[str] = None
    subevent: Optional[str] = None
    usetimefestival: Optional[str] = None
    
    # 여행코스 (contentTypeId=25)
    distance: Optional[str] = None
    infocentertourcourse: Optional[str] = None
    schedule: Optional[str] = None
    taketime: Optional[str] = None
    theme: Optional[str] = None
    
    # 레포츠 (contentTypeId=28)
    accomcountleports: Optional[str] = None
    chkbabycarriageleports: Optional[str] = None
    chkcreditcardleports: Optional[str] = None
    chkpetleports: Optional[str] = None
    expagerangeleports: Optional[str] = None
    infocenterleports: Optional[str] = None
    openperiod: Optional[str] = None
    parkingfeeleports: Optional[str] = None
    parkingleports: Optional[str] = None
    reservation: Optional[str] = None
    restdateleports: Optional[str] = None
    scaleleports: Optional[str] = None
    usefeeleports: Optional[str] = None
    usetimeleports: Optional[str] = None
    
    # 숙박 (contentTypeId=32)
    accomcountlodging: Optional[str] = None
    checkintime: Optional[str] = None
    checkouttime: Optional[str] = None
    chkcooking: Optional[str] = None
    foodplace: Optional[str] = None
    infocenterlodging: Optional[str] = None
    parkinglodging: Optional[str] = None
    pickup: Optional[str] = None
    roomcount: Optional[str] = None
    reservationlodging: Optional[str] = None
    reservationurl: Optional[str] = None
    roomtype: Optional[str] = None
    scalelodging: Optional[str] = None
    subfacility: Optional[str] = None
    
    # 숙박 부대시설
    barbecue: Optional[str] = None
    beauty: Optional[str] = None
    beverage: Optional[str] = None
    bicycle: Optional[str] = None
    campfire: Optional[str] = None
    fitness: Optional[str] = None
    karaoke: Optional[str] = None
    publicbath: Optional[str] = None
    publicpc: Optional[str] = None
    sauna: Optional[str] = None
    seminar: Optional[str] = None
    sports: Optional[str] = None
    refundregulation: Optional[str] = None
    
    # 쇼핑 (contentTypeId=38)
    chkbabycarriageshopping: Optional[str] = None
    chkcreditcardshopping: Optional[str] = None
    chkpetshopping: Optional[str] = None
    culturecenter: Optional[str] = None
    fairday: Optional[str] = None
    infocentershopping: Optional[str] = None
    opendateshopping: Optional[str] = None
    opentime: Optional[str] = None
    parkingshopping: Optional[str] = None
    restdateshopping: Optional[str] = None
    restroom: Optional[str] = None
    saleitem: Optional[str] = None
    saleitemcost: Optional[str] = None
    scaleshopping: Optional[str] = None
    shopguide: Optional[str] = None
    
    # 음식점 (contentTypeId=39)
    chkcreditcardfood: Optional[str] = None
    discountinfofood: Optional[str] = None
    firstmenu: Optional[str] = None
    infocenterfood: Optional[str] = None
    kidsfacility: Optional[str] = None
    opendatefood: Optional[str] = None
    opentimefood: Optional[str] = None
    packing: Optional[str] = None
    parkingfood: Optional[str] = None
    reservationfood: Optional[str] = None
    restdatefood: Optional[str] = None
    scalefood: Optional[str] = None
    seat: Optional[str] = None
    smoking: Optional[str] = None
    treatmenu: Optional[str] = None
    lcnsno: Optional[str] = None


class TourApiDetailImageDTO(BaseModel):
    """TourAPI 이미지정보 조회 응답 DTO"""
    contentid: str
    imgname: Optional[str] = None
    originimgurl: Optional[str] = None
    serialnum: Optional[str] = None
    cpyrhtDivCd: Optional[str] = None
    smallimageurl: Optional[str] = None


# 타입 매핑
TOURAPI_TO_TYPE_MAPPING = {
    "12": ("tourist_spot", "관광지"),
    "14": ("culture", "문화시설"),
    "15": ("festival_event", "축제/행사"),
    "25": ("course", "여행코스"),
    "28": ("leisure", "레포츠"),
    "32": ("accommodation", "숙박"),
    "38": ("shopping", "쇼핑"),
    "39": ("restaurant", "음식점")
}

# 기본 이미지 URL
DEFAULT_IMAGE_URL = "https://via.placeholder.com/500x333?text=No+Image"
DEFAULT_THUMBNAIL_URL = "https://via.placeholder.com/150x100?text=No+Image"
