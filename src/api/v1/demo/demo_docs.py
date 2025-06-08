# src/api/v1/demo/demo_docs.py

get_demo_docs = {
    "summary": "데모 단일 조회",
    "description": """
    주어진 `demo_id`에 해당하는 데모 데이터를 조회합니다.

    - 존재하지 않을 경우 404 오류 반환
    - 성공 시 `DemoReadDTO` 형태의 응답 반환

    **권장 사용 시점**:
    - 상세 보기 페이지 진입 시
    - 수정 시 기존 데이터 불러올 때
    """,
    "responses": {
        200: {
            "description": "데모 데이터 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "테스트 이름",
                        "content": "샘플 콘텐츠",
                        "test": "추가 필드"
                    }
                }
            }
        },
        404: {"description": "해당 demo_id에 대한 리소스를 찾을 수 없습니다."}
    }
}

create_demo_docs = {
    "summary": "데모 생성",
    "description": """
    새로운 데모 데이터를 생성합니다.

    - 요청 본문은 `DemoCreateDTO` 구조를 따라야 합니다.
    - 생성 성공 시 201 상태 코드와 성공 메시지를 반환합니다.

    **주의**: 필수 필드 누락 시 422 Validation 오류가 발생할 수 있습니다.
    """,
    "responses": {
        201: {
            "description": "데모 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "CREATED",
                        "message": "정상적으로 생성되었습니다."
                    }
                }
            }
        },
        422: {"description": "유효하지 않은 입력값입니다."}
    }
}

update_demo_docs = {
    "summary": "데모 수정",
    "description": """
    기존 데모 데이터를 수정합니다.

    - 요청 본문은 `DemoUpdateDTO` 구조를 따라야 합니다.
    - 존재하지 않는 demo_id인 경우 404 오류 발생
    - 일부 필드만 수정 가능하며, `exclude_unset=True`로 처리됩니다.

    **권장 사용 시점**:
    - 수정 폼 제출 시
    """,
    "responses": {
        200: {
            "description": "데모 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "정상적으로 수정되었습니다."
                    }
                }
            }
        },
        404: {"description": "해당 demo_id에 대한 리소스를 찾을 수 없습니다."},
        422: {"description": "입력값이 유효하지 않습니다."}
    }
}

delete_demo_docs = {
    "summary": "데모 삭제",
    "description": """
    주어진 demo_id에 해당하는 데모 데이터를 삭제합니다.

    - 삭제 성공 시 200 OK 응답
    - 존재하지 않는 ID일 경우 404 반환

    **주의사항**:
    - 삭제는 영구적으로 수행됩니다 (soft delete 아님)
    """,
    "responses": {
        200: {
            "description": "데모 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "status": "OK",
                        "message": "정상적으로 삭제되었습니다."
                    }
                }
            }
        },
        404: {"description": "해당 demo_id에 대한 리소스를 찾을 수 없습니다."}
    }
}