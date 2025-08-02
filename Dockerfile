# 가벼운 Python 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (최소한만)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install --no-cache-dir poetry

# Poetry 설정 (가상환경 생성하지 않음)
RUN poetry config virtualenvs.create false

# 의존성 파일들 먼저 복사 (Docker 레이어 캐싱 최적화)
COPY pyproject.toml poetry.lock* ./

# 프로덕션 의존성만 설치
RUN poetry install --only=main --no-interaction --no-ansi

# 소스 코드 복사
COPY src/ ./src/
COPY migrations/ ./migrations/

# 포트 설정 (Render는 $PORT 환경변수 사용)
EXPOSE $PORT

# FastAPI 실행 명령
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT