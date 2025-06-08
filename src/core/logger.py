import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os
from src.core.env import env

def setup_logger():
    log_file_path = Path(env.LOG_FILE_PATH).resolve() # 로그 파일 경로
    log_level = env.LOG_LEVEL.upper()                 # 로그 레벨 (ex: DEBUG, INFO, WARNING)
    log_to_console = env.LOG_TO_CONSOLE               # 콘솔 출력 여부

    # 로그 파일 저장 디렉토리 생성
    os.makedirs(log_file_path.parent, exist_ok=True)

    # 핸들러 리스트
    handlers = {}
    handler_names = []

    # 파일 헨들러
    if env.LOG_ROTATE:
        handlers["file"] = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": str(log_file_path),
            "when": "midnight",
            "backupCount": 7,
            "level": log_level,
            "encoding": "utf-8",
        }
    else:
        handlers["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": str(log_file_path),
            "level": log_level,
            "encoding": "utf-8",
        }
    handler_names.append("file")

    # 콘솔 헨들러
    if log_to_console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": log_level,
        }
        handler_names.append("console")

    # 로깅 구성
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(message)s"
            }
        },
        "handlers": handlers,
        "root": {
            "handlers": handler_names,
            "level": log_level,
        }
    }

    # 로깅 설정 적용
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """ 모듈별 로거 인스턴스를 가져오는 함수 """
    return logging.getLogger(name) # "__main__" 또는 "module.submodule" 같은 식별자를 가진 로거를 반환