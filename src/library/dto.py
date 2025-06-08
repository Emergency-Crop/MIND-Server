"""
DTO(Data Transfer Object) 공통 베이스 클래스 정의
모든 응답/요청 DTO 클래스가 상속받을 수 있는 BaseDTO 정의
"""
from pydantic import BaseModel

class BaseDTO(BaseModel):
    """
    DTO 공통 속성
    - orm_mode: SQLAlchemy ORM 객체를 자동으로 Pydantic 모델로 변환할 수 있도록 허용
    - use_enum_values: Enum 필드를 문자열이 아닌 값(value)으로 직렬화하여 반환
    """
    model_config = {
        "from_attributes": True,  # <- Pydantic v2에서 ORM 매핑용
        "use_enum_values": True
    }