"""
Travel API Module

통합 Travel API 모듈
- weather: 날씨 정보 조회
- attractions: 관광지 목록 조회
"""

from .travel_ctl import router
from . import weather_docs
from . import attractions_docs
from . import attractions_detail_docs

__all__ = ["router", "weather_docs", "attractions_docs", "attractions_detail_docs"]
