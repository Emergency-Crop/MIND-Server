"""
CORS 확장 모듈
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def use(app: FastAPI) -> None:
    """ FASTAPI 애플리케이션 CORS 미들웨어 적용 """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 운영 환경에서는 특정 origin만(도메인 URL) 허용
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],  # 클라이언트에서 읽을 수 있게 허용할 헤더
    )