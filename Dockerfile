# 빌드 스테이지
FROM python:3.11-slim as builder

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# Poetry 설정
RUN poetry config virtualenvs.create false

# 의존성 파일 복사
COPY pyproject.toml poetry.lock* ./

# requirements.txt 생성
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

# 런타임 스테이지
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 설치
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src/
COPY migrations/ ./migrations/

# 환경변수 기본값 설정
ENV PORT=8000

# 포트 노출
EXPOSE $PORT

# 소스 코드 복사
COPY src/ ./src/
COPY migrations/ ./migrations/

# 포트 설정 (Render는 $PORT 환경변수 사용)
EXPOSE $PORT

# FastAPI 실행 명령
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT