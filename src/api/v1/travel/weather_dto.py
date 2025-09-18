"""
Weather API DTO Module

/travel/weather API 전용 데이터 전송 객체 정의
- 명세서 기반 정확한 응답 구조 구현
- 원시 데이터, 파생 데이터, 표시 데이터 분리
"""

from pydantic import BaseModel, Field
from typing import Optional


class WeatherSourceDTO(BaseModel):
    """기상청 API 소스 정보"""
    provider: str = Field(default="KMA", description="데이터 제공자")
    api: str = Field(default="getUltraSrtNcst", description="호출된 API")
    baseDate: str = Field(..., description="기준일자(YYYY-MM-DD)")
    baseTime: str = Field(..., description="기준시각(HHMM, 정시)")
    nx: int = Field(..., description="격자 X좌표")
    ny: int = Field(..., description="격자 Y좌표")
    served_at: str = Field(..., description="데이터 제공 시각(ISO 8601)")
    note: Optional[str] = Field(None, description="데이터 생성/갱신 규칙 설명")


class WeatherAdminDTO(BaseModel):
    """행정구역 상세 정보"""
    level1: str = Field(..., description="시/도")
    level2: str = Field(..., description="시/군/구")
    level3: str = Field(..., description="읍/면/동")
    code: str = Field(..., description="행정구역 코드")
    nx: int = Field(..., description="매칭된 격자 X")
    ny: int = Field(..., description="매칭된 격자 Y")
    match_source: str = Field(..., description="매칭 방식: grid-only/grid+nearest/kd-nearest")
    distance_m: Optional[float] = Field(None, description="사용자 좌표 ↔ 중심점 거리(m)")
    confidence: Optional[float] = Field(None, description="0~1 신뢰도(거리 기반)")
    updated_at: Optional[str] = Field(None, description="엑셀 데이터 갱신일")


class WeatherLocationDTO(BaseModel):
    """위치 정보"""
    lat: float = Field(..., description="입력된 위도")
    lng: float = Field(..., description="입력된 경도")
    area_name: str = Field(..., description="행정구역명(시/군/구/동)")
    admin: WeatherAdminDTO = Field(..., description="행정구역 상세")


class WeatherCurrentDTO(BaseModel):
    """현재 날씨 정보"""
    temperature: float = Field(..., description="기온(℃, T1H)")
    temperature_text: str = Field(..., description="기온 표시 텍스트")
    humidity: int = Field(..., description="습도(%, REH)")
    humidity_text: str = Field(..., description="습도 표시 텍스트")
    precipitation_1h: float = Field(..., description="1시간 강수량(mm, RN1)")
    precipitation_text: str = Field(..., description="강수량 표시 텍스트")
    wind_speed: float = Field(..., description="풍속(m/s, WSD)")
    wind_speed_text: str = Field(..., description="풍속 표시 텍스트")
    wind_direction_deg: int = Field(..., description="풍향(deg, VEC)")
    wind_direction_16: str = Field(..., description="16방위 코드")
    wind_direction_text: str = Field(..., description="16방위 한글")
    wind_strength_text: str = Field(..., description="풍속 강도 텍스트")
    condition_pty_code: int = Field(..., description="강수형태 코드(PTY)")
    condition_pty_text: str = Field(..., description="강수형태 텍스트")
    condition_sky_code: Optional[int] = Field(None, description="SKY 코드(옵션)")
    condition_sky_text: Optional[str] = Field(None, description="SKY 텍스트(옵션)")
    icon: str = Field(..., description="날씨 아이콘(이모지)")


class WeatherRawDTO(BaseModel):
    """원시 데이터"""
    T1H: Optional[str] = Field(None, description="기온 원시값")
    RN1: Optional[str] = Field(None, description="1시간 강수량 원시값")
    REH: Optional[str] = Field(None, description="습도 원시값")
    WSD: Optional[str] = Field(None, description="풍속 원시값")
    VEC: Optional[str] = Field(None, description="풍향 원시값")
    PTY: Optional[str] = Field(None, description="강수형태 원시값")
    UUU: Optional[str] = Field(None, description="동서바람성분 원시값")
    VVV: Optional[str] = Field(None, description="남북바람성분 원시값")


class WeatherDerivedDTO(BaseModel):
    """파생 데이터"""
    is_travel_friendly: bool = Field(..., description="여행/야외활동 적합 여부")
    travel_advice: str = Field(..., description="상황별 조언")


class WeatherDataDTO(BaseModel):
    """날씨 데이터"""
    source: WeatherSourceDTO = Field(..., description="기상청 API 소스 정보")
    location: WeatherLocationDTO = Field(..., description="위치 정보")
    current: WeatherCurrentDTO = Field(..., description="현재 날씨 정보")
    raw: Optional[WeatherRawDTO] = Field(None, description="원시 데이터(raw=true일 때)")
    derived: WeatherDerivedDTO = Field(..., description="파생 데이터")
    updated_at: str = Field(..., description="최종 응답 생성 시각(ISO 8601)")


class WeatherResponseDTO(BaseModel):
    """날씨 API 응답"""
    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: WeatherDataDTO = Field(..., description="응답 데이터 객체")
