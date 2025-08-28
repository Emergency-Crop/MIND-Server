"""
감정 태그 추출 API 문서 모듈
"""
from fastapi.openapi.utils import get_openapi

# 감정 문장 분석 API 문서
analyze_emotion_sentences_docs = {
    "summary": "감정 문장 분석 및 아키타입 추출",
    "description": """
    여러 감정 문장을 입력받아 각각의 태그를 추출하고 전체 여행 아키타입을 분석하는 API입니다.
    
    **기능:**
    - 각 문장의 감정과 상황을 분석하여 태그 추출
    - 전체 문장의 태그를 종합하여 여행 아키타입 결정
    - 8가지 아키타입 중 가장 적합한 유형 반환
    
    **사용 예시:**
    ```json
    {
      "sentences": [
        {"index": 1, "feel": "진짜 거기 풍경 보고 말문이 턱 막혔어요, 너무 예뻐서요."},
        {"index": 2, "feel": "그냥 걷기만 해도 힐링 되는 곳이었어요, 마음이 편안해졌어요."}
      ]
    }
    ```
    
    **응답 예시:**
    ```json
    {
      "sentences": [
        {
          "index": 1,
          "feel": "진짜 거기 풍경 보고 말문이 턱 막혔어요, 너무 예뻐서요.",
          "tags": ["아름다움", "감동", "눈부심", "경이로움"]
        },
        {
          "index": 2,
          "feel": "그냥 걷기만 해도 힐링 되는 곳이었어요, 마음이 편안해졌어요.",
          "tags": ["편안함", "평온", "위로", "내적평화", "고요함"]
        }
      ],
      "overall_archetype": "힐링러"
    }
    ```
    """,
    "response_description": "각 문장별 분석 결과 및 전체 아키타입",
    "responses": {
        200: {
            "description": "성공적으로 분석 완료",
            "content": {
                "application/json": {
                    "example": {
                        "sentences": [
                            {
                                "index": 1,
                                "feel": "진짜 거기 풍경 보고 말문이 턱 막혔어요, 너무 예뻐서요.",
                                "tags": ["아름다움", "감동", "눈부심", "경이로움"]
                            },
                            {
                                "index": 2,
                                "feel": "그냥 걷기만 해도 힐링 되는 곳이었어요, 마음이 편안해졌어요.",
                                "tags": ["편안함", "평온", "위로", "내적평화", "고요함"]
                            }
                        ],
                        "overall_archetype": "힐링러"
                    }
                }
            }
        },
        400: {
            "description": "잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error": "문장이 비어있거나 너무 긴 경우"
                        }
                    }
                }
            }
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "서버 내부 오류가 발생했습니다."
                    }
                }
            }
        }
    }
}
