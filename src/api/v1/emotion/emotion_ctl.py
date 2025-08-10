"""
감정 태그 추출 API 컨트롤러 모듈
"""
from fastapi import APIRouter
from src.api.v1.emotion import emotion_svc
from src.api.v1.emotion.emotion_dto import (
    EmotionTagRequestDTO, EmotionAnalysisResponseDTO
)
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.emotion import emotion_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

router = APIRouter(
    prefix="/emotion",
    tags=["Emotion"],
    responses=Status.docs(ERR.BAD_REQUEST, ERR.INTERNAL_ERROR)
)

@router.post(
    "/analyze-sentences",
    response_model=EmotionAnalysisResponseDTO,
    **emotion_docs.analyze_emotion_sentences_docs
)
async def analyze_emotion_sentences(request_dto: EmotionTagRequestDTO):
    """
    여러 감정 문장을 입력받아 각각의 태그를 추출하고 전체 아키타입을 분석하는 API
    """
    try:
        result = await emotion_svc.emotion_service.analyze_emotion_sentences(request_dto)
        return result
        
    except ValueError as e:
        _logger.error(f"감정 분석 검증 오류: {str(e)}")
        raise ERR.BAD_REQUEST.to_exception({"error": str(e)})
    except Exception as e:
        _logger.error(f"감정 분석 중 예상치 못한 오류: {str(e)}")
        raise ERR.INTERNAL_ERROR.to_exception()
