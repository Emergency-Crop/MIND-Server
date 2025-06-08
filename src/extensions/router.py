"""
라우터 확장 모듈
"""
from fastapi import APIRouter
from src.core.api import MindAPI
from src.core.logger import get_logger

_logger = get_logger(__name__)

def use(app: MindAPI, base: str):
    """
    지정된 base 경로 하위의 *_ctl.py 파일들을 순회하며,
    각 모듈에서 정의된 APIRouter 인스턴스를 가져와 그룹으로 묶은 후,
    FastAPI 앱에 한 번에 등록
    """
    api_router = APIRouter()
    for router in app.iter_routers(base):
        _logger.debug(f"추가된 라우터 : {router.prefix}")
        api_router.include_router(router)

    app.include_router(api_router)