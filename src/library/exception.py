"""
FastAPI 기반의 API에서 공통된 예외 처리와 응답 포맷을 제공하기 위한 모듈

구성 요소:
- DescribedEnum      : 설명 문자열(desc)을 포함한 확장된 Enum
- ErrorMode          : 에러 코드(Enum) + HTTP 상태코드를 결합한 예외 정의용 클래스
- SuccessMode        : 성공 상태 코드 + 메시지를 담은 응답 정의용 클래스
- InvalidAPIUsage    : FastAPI의 HTTPException을 확장한 커스텀 예외
- APIResponse        : status, message, detail을 포함한 공통 API 응답 모델

사용 예:
- raise ERR.USER_NOT_FOUND.to_exception()
- return SUC.OK.to_response()
"""

from enum import Enum
from typing import Any, Optional, Union
from fastapi import HTTPException
from pydantic import BaseModel


class DescribedEnum(Enum):
    """
    desc(설명 문자열)를 갖는 확장된 Enum 클래스
    """

    def __init__(self, desc: str):
        self.desc = desc

    def __str__(self): return self.desc
    def __repr__(self): return self.desc

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other or self.desc == other
        return super().__eq__(other)


class ErrorMode(DescribedEnum):
    """
    에러 상태 코드 정의 (code + 설명)
    """

    def __init__(self, code: int, desc: str):
        super().__init__(desc)
        self.code = code

    def to_exception(
        self,
        detail: dict[str, str] = {},
        headers: Optional[dict[str, str]] = None
    ) -> HTTPException:
        return InvalidAPIUsage(status=self, detail=detail, headers=headers)


class InvalidAPIUsage(HTTPException):
    """
    ErrorMode를 기반으로 생성되는 FastAPI용 커스텀 예외
    """
    def __init__(
        self,
        status: ErrorMode,
        detail: dict[str, str] = {},
        headers: Optional[dict[str, str]] = None
    ):
        super().__init__(status_code=status.code, detail=detail, headers=headers)
        self.status = status.name
        self.message = status.desc


class SuccessMode(DescribedEnum):
    """
    성공 상태 코드 정의 (code + 설명)
    """

    def __init__(self, code: int, desc: str):
        super().__init__(desc)
        self.code = code

    def to_response(
        self,
        detail: dict[str, Any] = {},
    ) -> "APIResponse":
        return APIResponse(status=self.name, message=self.desc, detail=detail)


class APIResponse(BaseModel):
    """
    API 응답 포맷 모델
    - status: 상태 이름
    - message: 상태 설명
    - detail: 상세 정보
    """
    status: str
    message: str
    detail: Union[dict[str, Any], str] = {}