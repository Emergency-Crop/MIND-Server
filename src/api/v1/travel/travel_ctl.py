"""
Travel Controller Module

통합 Travel API 라우터 - weather와 attractions 컨트롤러를 통합
- /travel/weather: 날씨 정보 조회 (weather_ctl.py)
- /travel/attractions: 주변 관광지 목록 조회 (attractions_ctl.py)
"""

from fastapi import APIRouter
from src.api.v1.travel import weather_ctl
from src.api.v1.travel import attractions_ctl
from src.api.v1.travel import attractions_detail_ctl

# Travel API 라우터
router = APIRouter()

# 하위 라우터들을 포함 (엔드포인트는 /travel/weather, /travel/attractions, /travel/attractions/{contentId}로 유지)
router.include_router(weather_ctl.weather_router, prefix="/travel", tags=["Weather"])
router.include_router(attractions_ctl.attractions_router, prefix="/travel", tags=["Attractions"])
router.include_router(attractions_detail_ctl.attractions_detail_router, prefix="/travel", tags=["Attractions Detail"])