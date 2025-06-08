"""
RDB 세션 관리 객체(런타임에) 초기화
"""
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.rdb.provider import RDBSessionManager
from src.core.env import env

# 비동기 SQLAlchemy 엔진 생성
_engine = create_async_engine(
    f"{env.DB_PROTOCOL}://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}",
    echo=True,
    future=True
)

# 세션 팩토리(세션 생성기) 정의
_session_factory = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

rdbs = RDBSessionManager(_engine, _session_factory)