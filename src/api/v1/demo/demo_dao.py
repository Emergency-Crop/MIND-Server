"""
Demo DAO Module

- DB와 직접 통신하는 쿼리 로직을 담당
"""
from sqlalchemy import select, insert, update, delete
from sqlalchemy.engine import ScalarResult
from typing import Optional
from src.config.rdb.models import Demo
from src.api.v1.demo.demo_dto import DemoCreateDTO, DemoUpdateDTO
from src.config.rdb.session import rdbs, AsyncSession
from src.core.logger import get_logger

_logger = get_logger(__name__)

@rdbs.dao()
async def fetch_by_id(demo_id: int, db: AsyncSession = rdbs.di()) -> Optional[Demo]:
    """
    demo_id에 해당하는 Demo 레코드를 조회합니다.
    """
    result: ScalarResult = await db.scalars(
        select(Demo).where(Demo.id == demo_id)
    )
    return result.first()


@rdbs.dao(tx=True)
async def insert_demo(dto: DemoCreateDTO, db: AsyncSession = rdbs.di()) -> Demo:
    """
    DemoCreateDTO 데이터를 기반으로 새로운 Demo 레코드를 생성합니다.
    - RETURNING으로 삽입된 Demo 객체 반환
    """
    result = await db.execute(
        insert(Demo)
        .values(dto.model_dump())
        .returning(Demo)  # 삽입된 row 반환
    )
    return result.scalar_one()


@rdbs.dao(tx=True)
async def update_demo(demo_id: int, dto: DemoUpdateDTO, db: AsyncSession = rdbs.di()) -> Optional[Demo]:
    """
    demo_id에 해당하는 Demo 레코드를 주어진 dto로 수정합니다.
    """
    demo = await db.get(Demo, demo_id)
    if not demo:
        return None
    for k, v in dto.model_dump(exclude_unset=True).items():
        setattr(demo, k, v)
    return demo


@rdbs.dao(tx=True)
async def delete_demo(demo_id: int, db: AsyncSession = rdbs.di()) -> Optional[Demo]:
    """
    demo_id에 해당하는 Demo 레코드를 삭제합니다.
    """
    demo = await db.get(Demo, demo_id)
    if not demo:
        return None
    await db.delete(demo)
    return demo