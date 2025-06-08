"""
Demo Service Module

- DB 액세스를 포함한 비즈니스 로직 처리
"""
from src.api.v1.demo import demo_dao
from src.api.v1.demo.demo_dto import DemoCreateDTO, DemoUpdateDTO
from src.config.rdb.models import Demo
from typing import Optional
from src.core.logger import get_logger

_logger = get_logger(__name__)


async def get_demo(demo_id: int) -> Optional[Demo]:
    return await demo_dao.fetch_by_id(demo_id)


async def create_demo(dto: DemoCreateDTO) -> int:
    demo = await demo_dao.insert_demo(dto)
    return demo.id


async def update_demo(demo_id: int, dto: DemoUpdateDTO) -> Optional[Demo]:
    return await demo_dao.update_demo(demo_id, dto)


async def delete_demo(demo_id: int) -> Optional[Demo]:
    return await demo_dao.delete_demo(demo_id)