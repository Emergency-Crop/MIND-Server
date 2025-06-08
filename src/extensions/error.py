"""
FastAPI 전역 예외 처리를 위한 모듈
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from src.library.exception import InvalidAPIUsage, APIResponse
from src.config.status import ERR

import logging

logger = logging.getLogger(__name__)


def use(app: FastAPI):
    """
    FastAPI 앱에 전역 예외 핸들러 등록
    """

    @app.exception_handler(InvalidAPIUsage)
    async def handle_custom_api_exception(request: Request, exc: InvalidAPIUsage):
        """
        커스텀 예외 처리 (InvalidAPIUsage)
        """
        logger.warning(f"[{exc.status}] {exc.message} - detail={exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=APIResponse(
                status=exc.status,
                message=exc.message,
                detail=exc.detail
            ).dict()
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        """
        FastAPI 기본 HTTPException 처리
        - 404 등 직접 raise하지 않은 예외에도 대응
        """
        logger.error(f"[HTTPException] {exc.status_code} - {exc.detail}")
        detail = exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
        return JSONResponse(
            status_code=exc.status_code,
            content=APIResponse(
                status="HTTP_EXCEPTION",
                message=detail.get("message", "요청 처리 중 오류가 발생했습니다."),
                detail=detail
            ).dict()
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception):
        """
        모든 예상치 못한 예외 처리
        - 500 INTERNAL_SERVER_ERROR
        """
        logger.exception(f"[Unhandled Exception] {exc}")
        return JSONResponse(
            status_code=ERR.INTERNAL_SERVER_ERROR.code,
            content=APIResponse(
                status=ERR.INTERNAL_SERVER_ERROR.name,
                message=ERR.INTERNAL_SERVER_ERROR.desc,
                detail={"error": str(exc)}
            ).dict()
        )