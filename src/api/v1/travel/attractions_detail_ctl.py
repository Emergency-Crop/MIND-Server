"""
Attractions Detail Controller Module

관광지 상세 정보 조회 API의 HTTP 요청/응답 처리
- /travel/attractions/{contentId}: 관광지 상세 정보 조회
"""

from fastapi import APIRouter, Path, HTTPException
from src.api.v1.travel.attractions_detail_service import attractions_detail_service
from src.api.v1.travel.attractions_detail_dto import AttractionDetailResponseDTO
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.travel import attractions_detail_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

# Attractions Detail API 라우터
attractions_detail_router = APIRouter()


@attractions_detail_router.get(
    "/attractions/{content_id}",
    response_model=APIResponse,
    summary="관광지 상세 정보 조회",
    description=attractions_detail_docs.get_attraction_detail_docs["description"],
    responses=attractions_detail_docs.get_attraction_detail_docs["responses"]
)
async def get_attraction_detail(
    content_id: str = Path(
        ..., 
        description="관광지 고유 ID (주변 관광지 목록 조회 API에서 획득)",
        example="126508",
        min_length=1,
        max_length=20
    )
):
    """
    특정 관광지의 상세 정보를 조회합니다.
    
    ## 파라미터 설명
    
    - **content_id**: 관광지 고유 ID (주변 관광지 목록 조회 API에서 획득)
    
    ## 응답 정보
    
    - **기본 정보**: 관광지명, 타입, 요약, 상세 설명
    - **이미지 정보**: 대표 이미지, 추가 이미지 목록
    - **위치 정보**: 주소, GPS 좌표
    - **연락처 정보**: 전화번호, 웹사이트
    - **운영 정보**: 평점, 운영 상태, 운영시간, 휴무일, 입장료
    - **편의시설**: 주차, 휠체어 접근, 유모차, 반려동물, 와이파이 등
    - **부가 정보**: 태그, 방문 팁, 주변 관광지, 교통 정보
    
    ## Rate Limiting
    
    - 분당 요청: 30회 (IP 주소별)
    - 시간당 요청: 500회 (API 키별)
    - 일일 요청: 5,000회 (API 키별)
    
    ## 활용 외부 API
    
    - 한국관광공사 국문 관광정보 서비스:
        - detailCommon2 (공통정보 조회)
        - detailIntro2 (소개정보 조회)
        - detailImage2 (이미지정보 조회)
        - locationBasedList2 (주변 관광지 조회)
    """
    try:
        _logger.info(f"Attraction Detail API 요청: content_id={content_id}")
        
        # 서비스 호출
        result = await attractions_detail_service.get_attraction_detail(content_id)
        
        # 응답 데이터 변환
        response_data = result.model_dump()
        
        # 성공 응답
        final_response = SUC.OK.to_response(detail=response_data)
        
        return final_response
        
    except ValueError as e:
        # 유효성 검증 오류
        _logger.error(f"❌ Attraction Detail validation error: {str(e)}")
        raise ERR.BAD_REQUEST.to_exception(
            detail={
                "error": "INVALID_CONTENT_ID",
                "message": "유효하지 않은 관광지 ID입니다.",
                "details": {"error": str(e)}
            }
        )
    except HTTPException as e:
        # 서비스에서 발생한 HTTPException은 그대로 전달
        _logger.error(f"❌ Attraction Detail HTTPException: {str(e)}")
        raise e
    except Exception as e:
        # 예상치 못한 오류
        _logger.error(f"❌ Attraction Detail API error: {str(e)}")
        raise ERR.INTERNAL_ERROR.to_exception(
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        )


# 자동 라우터 로딩을 위한 별칭
router = attractions_detail_router
