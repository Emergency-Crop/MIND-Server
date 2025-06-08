"""
모든 요청을 감싸는 예외 처리 미들웨어를 정의
서버에서 발생하는 예외를 한 곳에서 잡고, 일관된 에러 응답과 로그를 제공
"""
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.core.logger import get_logger

_logger = get_logger(__name__)

def use(app: FastAPI):
    """
    FastAPI 앱에 커스텀 미들웨어를 등록하는 함수
    - 모든 요청(request)을 가로채고 예외를 처리함.
    - 서버 코드에서 발생한 예상치 못한 에러도 잡아내어 로깅하고, 클라이언트에 명확한 에러 메시지를 제공함.
    """
    @app.middleware("http")
    async def custom_filter_middleware(request: Request, call_next):
        try:
            # 정상적인 요청 흐름: 다음 라우터 혹은 미들웨어로 전달
            return await call_next(request)
        except Exception as err:  # 예상하지 못한 모든 예외 처리
            # 서버 로그에 예외 내용을 기록
            _logger.exception(err)

            # 클라이언트에게 JSON 형식으로 500 에러 응답 전송
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder({
                    "detail": str(err)  # 예외 메시지를 그대로 detail로 전달
                }),
            )