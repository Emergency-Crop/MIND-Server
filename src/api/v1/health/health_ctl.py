from fastapi import APIRouter
from src.api.v1.health import health_svc
from src.api.v1.health.health_dto import HealthReadDTO
from src.config.status import ERR
from src.library.helper import Status
from src.api.v1.health import health_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses=Status.docs(ERR.SERVICE_UNAVAILABLE)  # 기본적으로 503 Service Unavailable 응답 가능
)


@router.get(
    "/",
    response_model=HealthReadDTO,
    **health_docs.get_health_docs
)
async def get_health():
    """
    서버의 정상 동작 여부를 확인하는 헬스체크 API
    """
    health_data = await health_svc.get_health_status()
    if not health_data:
        raise ERR.NOT_FOUND.to_exception({"message": "Health status not available"})
    return HealthReadDTO.model_validate(health_data)
