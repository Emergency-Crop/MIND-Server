"""
FastAPI 진입점
"""
# import uvicorn
from src.core.api import MindAPI
from src.core.logger import setup_logger, get_logger
from src.extensions import lifespan, cors, router, filter, error
from src.core.env import env

# 로깅 설정
setup_logger()
_logger = get_logger(__name__)


# MindAPI 인스턴스 생성
app = MindAPI(
    title="MIND API Server",
    description="MIND API 서버 입니다.",
    version="1.0.0",
    docs_url="/docs" if env.API_DOC_VIEW else None,
    redoc_url="/redoc" if env.API_DOC_VIEW else None,
    # contact={
    #     "name": "Your Name",
    #     "url": "https://yourdomain.com",
    #     "email": "your@email.com"
    # },
    # license_info={
    #     "name": "MIT",
    #     "url": "https://opensource.org/licenses/MIT"
    # }
)

# 확장 기능 추가
app.add_extension(lifespan)
app.add_extension(cors)
app.add_extension(filter)
app.add_extension(error)
app.add_extension(router, base="./src/api/v1")

_logger.info(f"FastAPI 서버 시작 중 ... (DB : {env.DB_NAME})")

# if __name__ == "__main__":
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)