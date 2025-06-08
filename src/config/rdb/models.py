"""
RDB 스키마 정의
"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.config.rdb.provider import Base

class Demo(Base):
    """
    개발 환경 구축을 위해 만들어둔 데모용 임시 테이블
    (추후 RDB 관련 논의 이후 삭제할 예정)
    """
    __tablename__ = "demo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    test: Mapped[str] = mapped_column(String(100), nullable=False)

metadata = Base.metadata