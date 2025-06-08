"""
비동기 RDB 세션 관리 모듈
"""
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import AsyncGenerator

class Base(DeclarativeBase):
    """
    모든 SQLAlchemy 모델의 공통 부모, metadata 등록, Alembic 마이그레이션 인식, 테이블 생성 등 기능 상속
    """
    pass

class RDBSessionManager:
    """
    비동기 세션 매니저. 서버 시작 시 테이블 생성 및 연결 관리
    """

    def __init__(self, engine: AsyncEngine, factory: sessionmaker):
        self._engine = engine
        self._factory = factory
        self._meta = Base

    async def dispose(self):
        """ DB 세션 연결 해제 """
        await self._engine.dispose()

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """ 조회용: FastAPI Depends용 비동기 세션 """
        async with self._factory() as session:
            yield session

    async def get_tx_session(self) -> AsyncGenerator[AsyncSession, None]:
        """ 쓰기용: FastAPI Depends용 트랜잭션 세션 """
        async with self._factory() as session:
            async with session.begin():
                yield session

    def di(self, tx: bool = False):
        """
        FastAPI Depends에서 사용할 수 있도록 의존성 주입용 함수 반환
        예시:
        - db: Annotated[AsyncSession, Depends(rdbs.di())]
        """
        return self.get_tx_session if tx else self.get_db_session

    def dao(self, tx: bool = False):
        """
        DAO 함수 데코레이터
        - 세션 생성 및 주입
        - tx=True일 경우 자동 트랜잭션 begin/commit
        - 예외 발생 시 자동 rollback
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                async with self._factory() as session:
                    try:
                        if tx:
                            async with session.begin():
                                result = await func(*args, db=session, **kwargs)
                        else:
                            result = await func(*args, db=session, **kwargs)
                        return result
                    except Exception:
                        await session.rollback()
                        raise
            return wrapper
        return decorator