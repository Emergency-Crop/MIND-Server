"""
FastAPI 애플리케이션 생명주기 관리 모듈
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config.rdb.session import rdbs

def use(app: FastAPI):
    """ FastAPI lifespan을 주입하는 확장 모듈 """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """ FastAPI 애플리케이션 생명주기 (startup, shutdown) 관리 """
        yield # 앱 실행 중
        await rdbs.dispose()

    app.router.lifespan_context = lifespan