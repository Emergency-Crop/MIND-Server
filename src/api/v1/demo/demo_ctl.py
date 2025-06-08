from fastapi import APIRouter
from src.api.v1.demo import demo_svc
from src.api.v1.demo.demo_dto import DemoCreateDTO, DemoUpdateDTO, DemoReadDTO
from src.library.exception import APIResponse
from src.config.status import SUC, ERR
from src.library.helper import Status
from src.api.v1.demo import demo_docs
from src.core.logger import get_logger

_logger = get_logger(__name__)

router = APIRouter(
    prefix="/demo",
    tags=["Demo"],
    responses=Status.docs(ERR.NOT_FOUND)
)


@router.get(
    "/{demo_id}",
    response_model=DemoReadDTO,
    **demo_docs.get_demo_docs
)
async def get_demo(demo_id: int):
    demo = await demo_svc.get_demo(demo_id)
    if not demo:
        raise ERR.NOT_FOUND.to_exception({"demo_id": str(demo_id)})
    return DemoReadDTO.model_validate(demo)


@router.post(
    "/",
    response_model=APIResponse,
    status_code=SUC.CREATED.code,
    **demo_docs.create_demo_docs
)
async def create_demo(dto: DemoCreateDTO):
    demo_id = await demo_svc.create_demo(dto)
    return SUC.CREATED.to_response(detail={"id": demo_id})


@router.put(
    "/{demo_id}",
    response_model=APIResponse,
    **demo_docs.update_demo_docs
)
async def update_demo(demo_id: int, dto: DemoUpdateDTO):
    updated = await demo_svc.update_demo(demo_id, dto)
    if not updated:
        raise ERR.NOT_FOUND.to_exception({"demo_id": str(demo_id)})
    return SUC.OK.to_response()


@router.delete(
    "/{demo_id}",
    response_model=APIResponse,
    **demo_docs.delete_demo_docs
)
async def delete_demo(demo_id: int):
    deleted = await demo_svc.delete_demo(demo_id)
    if not deleted:
        raise ERR.NOT_FOUND.to_exception({"demo_id": str(demo_id)})
    return SUC.OK.to_response()