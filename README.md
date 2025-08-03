<p align="center">
  <br>
  <img width="400" src="" alt="MIND 로고">
  <br>
  <br>
</p>

<h2 align='center'>MIND Server</h2>

<p align='center'>
2025 공공데이터활용 공모전 <a href='' target="_blank">링크</a>
<br><br>

<p align='center'>
<i>Created by: 구황작물<a href='링크 경로' target="_blank">링크</a></i>
<br><br>

<div align="center" style="line-height: 1;">
<a href='https://github.com/' target="_blank">
<img src='이미지 경로' alt='스킬 혹은 참고링크'>
</a>
</div>

</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. Introduction](#1-introduction)
- [2. Preview](#2-preview)
- [3. Features](#3-features)
- [4. Quick Start](#4-quick-start)
  - [Docker를 사용한 배포](#docker를-사용한-배포)
  - [Render 배포](#render-배포)
- [5. How to Use](#5-how-to-use)
- [6. Contact](#6-contact)

## 1. Introduction

## 2. Preview

## 3. Features

## 4. Quick Start

### Docker를 사용한 배포

1. **환경 변수 설정**
   ```bash
   # .env 파일 생성
   DB_USER=mind_user
   DB_PASSWORD=your_secure_password
   DB_HOST=db
   DB_PORT=5432
   DB_NAME=mind_db
   TOUR_API_KEY=your_tour_api_key_here
   API_DOC_VIEW=true
   LOG_LEVEL=INFO
   MODE=production
   ```

2. **Docker Compose로 실행**
   ```bash
   docker-compose up -d
   ```

3. **개별 Docker 이미지로 실행**
   ```bash
   # 이미지 빌드
   docker build -t mind-api .
   
   # 컨테이너 실행
   docker run -d \
     --name mind-api \
     -p 8000:8000 \
     -e DB_USER=mind_user \
     -e DB_PASSWORD=your_password \
     -e DB_HOST=your_db_host \
     -e DB_NAME=mind_db \
     -e TOUR_API_KEY=your_api_key \
     mind-api
   ```

### Render 배포

1. **Render 대시보드에서 새 Web Service 생성**
2. **GitHub 저장소 연결**
3. **환경 변수 설정**
   - `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`
   - `TOUR_API_KEY`
   - `MODE=production`
4. **빌드 명령어**: `docker build -t mind-api .`
5. **실행 명령어**: `docker run -p $PORT:8000 mind-api`

## 5. How to Use

## 6. Contact