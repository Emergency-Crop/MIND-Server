"""
Demo DTO 모듈

- Create, Update, Read 요청/응답 스키마 정의
"""

from pydantic import Field
from src.library.dto import BaseDTO


class DemoCreateDTO(BaseDTO):
    """
    새로운 Demo 객체 생성을 위한 요청 DTO
    """
    name: str = Field(..., description="데모 이름", example="홍길동")
    content: str = Field(..., description="본문 내용", example="이것은 예제입니다.")
    test: str = Field(..., description="테스트용 추가 필드", example="테스트 값")


class DemoUpdateDTO(BaseDTO):
    """
    Demo 객체 수정을 위한 요청 DTO
    """
    name: str = Field(None, description="수정할 이름")
    content: str = Field(None, description="수정할 본문")
    test: str = Field(None, description="수정할 테스트 값")


class DemoReadDTO(BaseDTO):
    """
    단일 조회 응답용 DTO
    """
    id: int
    name: str
    content: str
    test: str

    model_config = {"from_attributes": True}