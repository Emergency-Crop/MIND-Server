"""
Weather Controller Module

HTTP 요청/응답 처리, 파라미터 검증, 에러 핸들링을 담당하는 컨트롤러
- /travel/weather: 날씨 정보 조회
"""
from fastapi import APIRouter, Query, HTTPException
from src.api.v1.travel.weather_service import WeatherService
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.travel import weather_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

# Weather API 라우터
weather_router = APIRouter()


@weather_router.get(
    "/weather",
    response_model=APIResponse,
    summary="GPS 기반 현재 날씨 정보 조회",
    description=weather_docs.get_weather_docs["description"],
    responses=weather_docs.get_weather_docs["responses"]
)
async def get_weather(
    lat: float = Query(
        ..., 
        ge=33.0, 
        le=39.0, 
        description="사용자 위치의 위도 (33.0 ~ 39.0)",
        example=37.5665
    ),
    lng: float = Query(
        ..., 
        ge=124.0, 
        le=132.0, 
        description="사용자 위치의 경도 (124.0 ~ 132.0)",
        example=126.9780
    )
):
    """
    사용자의 GPS 위치를 기반으로 현재 날씨 정보를 조회합니다.
    
    ## 파라미터 설명
    
    - **lat**: 사용자 위치의 위도 (33.0 ~ 39.0)
    - **lng**: 사용자 위치의 경도 (124.0 ~ 132.0)
    
    ## Rate Limiting
    
    - 분당 요청: 30회 (IP 주소별)
    - 시간당 요청: 500회 (API 키별)
    - 일일 요청: 5,000회 (API 키별)
    
    ## 활용 외부 API
    
    - 기상청 초단기실황조회 API (getUltraSrtNcst)
    """
    try:
        _logger.info(f"Weather API 요청: lat={lat}, lng={lng}")
        
        # WeatherService 인스턴스 생성
        weather_service = WeatherService()
        
        # 서비스 호출
        result = await weather_service.get_weather(lat, lng)
        
        # 응답 데이터 변환
        response_data = result.model_dump()
        
        # 성공 응답
        final_response = SUC.OK.to_response(detail=response_data)
        
        return final_response
        
    except ValueError as e:
        # 유효성 검증 오류
        _logger.error(f"❌ Weather validation error: {str(e)}")
        raise ERR.BAD_REQUEST.to_exception(
            detail={
                "error": "INVALID_COORDINATES",
                "message": "유효하지 않은 GPS 좌표입니다.",
                "details": {"error": str(e)}
            }
        )
    except HTTPException as e:
        # 서비스에서 발생한 HTTPException은 그대로 전달
        _logger.error(f"❌ Weather HTTPException: {str(e)}")
        raise e
    except Exception as e:
        # 예상치 못한 오류
        _logger.error(f"❌ Weather API error: {str(e)}")
        raise ERR.INTERNAL_ERROR.to_exception(
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        )


# 자동 라우터 로딩을 위한 별칭
router = weather_router
