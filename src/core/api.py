"""
FastAPI 래퍼 클래스 및 자동 라우터 로딩 기능 포함
"""
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from fastapi import APIRouter, FastAPI
import logging

logger = logging.getLogger(__name__)

class MindAPI(FastAPI):
    """
    FastAPI 기능을 확장한 커스텀 클래스
    """

    def __init__(self, **kwargs):
        # disable_api_doc=True 옵션이 있으면 문서 URL 비활성화
        if kwargs.get('disable_api_doc', None):
            kwargs.update({"redoc_url": None, "docs_url": None})
        super().__init__(**kwargs)

    def add_extension(self, extend, *args, **kwargs):
        """
        확장 기능 클래스 등록
        (예: 미들웨어, 커스텀 훅 등을 주입하고 싶을 때 사용)
        전달받은 extend의 use 메서드 호출함. 확장 모듈은 반드시 use() 이름으로 작성할 것
        """
        extend.use(self, *args, **kwargs)

    def _get_module_name(self, path: Path) -> str:
        """
        파일 경로에서 Python 모듈 경로 문자열 생성
        예: /src/api/v1/user_ctl.py → src.api.v1.user_ctl

        경로 상에 __init__.py 가 존재하는 폴더만 모듈로 인식
        """
        paths = []

        # 현재 파일이 __init__.py가 아니라면 파일명 추가
        if path.name != '__init__.py':
            paths.append(path.stem)

        # 부모 폴더를 따라 올라가며 모듈 경로 구성
        while True:
            path = path.parent
            if not path or not path.is_dir():
                break

            # __init__.py가 없으면 모듈 경로에서 제외
            if not any(f.name == '__init__.py' for f in path.iterdir()):
                break

            paths.append(path.stem)

        return '.'.join(reversed(paths))

    def _load_module(self, module_name: str, attr_name: str) -> Optional[APIRouter]:
        """
        모듈 경로에서 해당 속성(attr_name)을 가져옴
        예: src.api.v1.user_ctl 모듈에서 ns 라우터 가져오기
        """
        try:
            logger.debug(f"Loading module: {module_name}, attribute: {attr_name}")
            module = __import__(module_name, fromlist=[attr_name])
            attr = getattr(module, attr_name)
            return attr
        except (ModuleNotFoundError, AttributeError) as e:
            logger.warning(f"Failed to load '{attr_name}' from {module_name}: {e}")
            return None

    def iter_routers(self, base: str):
        """
        지정된 폴더 하위 *_ctl.py에서 'router' 이름의 APIRouter를 자동으로 등록
        """
        for file in Path(base).glob("**/*_ctl.py"):
            module_name = self._get_module_name(file)
            router = self._load_module(module_name, "router")
            if isinstance(router, APIRouter):
                yield router
            else:
                logger.warning(f"'router' not found or invalid in {module_name}")

    def wrap_with(self, wrapper_fn: Optional[Callable[..., Any]] = None):
        """
        AOP 데코레이터 팩토리
        - FastAPI 라우터 함수에 공통 전/후처리 로직을 끼워 넣을 수 있음
        - fn: (original_func, *args, **kwargs) 형태의 비동기 함수 전달
        """
        def decorator(fn):
            @wraps(fn)
            async def wrapper(*args, **kwargs):
                # 래핑 함수가 있으면 중간에 끼워넣고, 없으면 원본 함수 그대로 실행
                if wrapper_fn:
                    return await wrapper_fn(fn, *args, **kwargs)
                return await fn(*args, **kwargs)

            return wrapper

        return decorator