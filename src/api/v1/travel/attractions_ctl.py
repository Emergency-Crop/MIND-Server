"""
Attractions Controller Module

HTTP 요청/응답 처리, 파라미터 검증, 에러 핸들링을 담당하는 컨트롤러
- /travel/attractions: 주변 관광지 목록 조회
"""
from fastapi import APIRouter, Query, HTTPException
from src.api.v1.travel.attractions_service import attractions_service
from src.api.v1.travel.attractions_dto import (
    AttractionsRequestDTO, AttractionsCategoryEnum, AttractionsSortEnum
)
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.travel import attractions_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

# Attractions API 라우터
attractions_router = APIRouter()


@attractions_router.get(
    "/attractions",
    response_model=APIResponse,
    summary="주변 관광지 목록 조회",
    description=attractions_docs.get_attractions_docs["description"],
    responses=attractions_docs.get_attractions_docs["responses"]
)
async def get_nearby_attractions(
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
    ),
    radius: int = Query(
        default=2, 
        ge=1, 
        le=20, 
        description="검색 반경 (km 단위, 기본값: 2, 최대: 20)",
        example=5
    ),
    category: AttractionsCategoryEnum = Query(
        default=AttractionsCategoryEnum.ALL, 
        description="관광지 유형 (all, tourist, culture, festival, course, leisure, accommodation, shopping, restaurant, 기본값: all)",
        example="all"
    ),
    sort: AttractionsSortEnum = Query(
        default=AttractionsSortEnum.DISTANCE, 
        description="정렬 방식 (distance, name, rating, 기본값: distance)",
        example="distance"
    ),
    limit: int = Query(
        default=20, 
        ge=1, 
        le=50, 
        description="반환할 최대 결과 수 (기본값: 20, 최대: 50)",
        example=20
    ),
    offset: int = Query(
        default=0, 
        ge=0, 
        description="결과 시작 위치 (기본값: 0, 페이지네이션용)",
        example=0
    )
):
    """
    사용자의 GPS 위치를 기반으로 주변 관광지 목록을 조회합니다.
    
    ## 파라미터 설명
    
    - **lat**: 사용자 위치의 위도 (33.0 ~ 39.0)
    - **lng**: 사용자 위치의 경도 (124.0 ~ 132.0)  
    - **radius**: 검색 반경 (km 단위, 기본값: 2, 최대: 20)
    - **category**: 관광지 유형 (all, tourist, culture, festival, course, leisure, accommodation, shopping, restaurant)
    - **sort**: 정렬 방식 (distance, name, rating)
    - **limit**: 반환할 최대 결과 수 (기본값: 20, 최대: 50)
    - **offset**: 결과 시작 위치 (기본값: 0, 페이지네이션용)
    
    ## 카테고리 매핑표
    
    | 클라이언트 요청값 | 설명 | 한국관광공사 코드 |
    |------------------|------|-------------------|
    | all | 전체 | - |
    | tourist | 관광지 | 12 |
    | culture | 문화시설 | 14 |
    | festival | 축제/행사 | 15 |
    | course | 여행코스 | 25 |
    | leisure | 레포츠 | 28 |
    | accommodation | 숙박 | 32 |
    | shopping | 쇼핑 | 38 |
    | restaurant | 음식점 | 39 |
    
    ## Rate Limiting
    
    - 분당 요청: 30회 (IP 주소별)
    - 시간당 요청: 500회 (API 키별)
    - 일일 요청: 5,000회 (API 키별)
    
    ## 활용 외부 API
    
    - 한국관광공사 국문 관광정보 서비스: locationBasedList2
    """
    try:
        _logger.info(f"Attractions API 요청: lat={lat}, lng={lng}, radius={radius}km")
        
        # 요청 DTO 생성
        request_dto = AttractionsRequestDTO(
            lat=lat,
            lng=lng,
            radius=radius,
            category=category,
            sort=sort,
            limit=limit,
            offset=offset
        )
        
        # 서비스 호출
        result = await attractions_service.get_nearby_attractions(request_dto)
        
        # 응답 데이터 변환
        response_data = result.model_dump()
        
        # 성공 응답
        final_response = SUC.OK.to_response(detail=response_data)
        
        return final_response
        
    except ValueError as e:
        # 유효성 검증 오류
        _logger.error(f"❌ Attractions validation error: {str(e)}")
        raise ERR.BAD_REQUEST.to_exception(
            detail={
                "error": "INVALID_PARAMETERS",
                "message": "잘못된 요청 파라미터입니다.",
                "details": {"error": str(e)}
            }
        )
    except HTTPException as e:
        # 서비스에서 발생한 HTTPException은 그대로 전달
        _logger.error(f"❌ Attractions HTTPException: {str(e)}")
        raise e
    except Exception as e:
        # 예상치 못한 오류
        _logger.error(f"❌ Attractions API error: {str(e)}")
        raise ERR.INTERNAL_ERROR.to_exception(
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        )


# 자동 라우터 로딩을 위한 별칭
router = attractions_router
