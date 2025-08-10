"""
감정 태그 추출 API DTO 모듈
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class EmotionSentenceDTO(BaseModel):
    """감정 문장 DTO"""
    index: int = Field(..., description="문장 인덱스")
    feel: str = Field(..., description="감정 문장", min_length=1, max_length=1000)

class EmotionTagRequestDTO(BaseModel):
    """감정 태그 추출 요청 DTO (다중 문장용)"""
    sentences: List[EmotionSentenceDTO] = Field(..., description="감정 분석할 문장들")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentences": [
                    {"index": 1, "feel": "진짜 거기 풍경 보고 말문이 턱 막혔어요, 너무 예뻐서요."},
                    {"index": 2, "feel": "그냥 걷기만 해도 힐링 되는 곳이었어요, 마음이 편안해졌어요."}
                ]
            }
        }

class EmotionSentenceResultDTO(BaseModel):
    """감정 문장 결과 DTO"""
    index: int = Field(..., description="문장 인덱스")
    feel: str = Field(..., description="원본 감정 문장")
    tags: List[str] = Field(..., description="추출된 감정 태그 목록")

class EmotionAnalysisResponseDTO(BaseModel):
    """감정 분석 전체 응답 DTO"""
    sentences: List[EmotionSentenceResultDTO] = Field(..., description="각 문장별 분석 결과")
    overall_archetype: str = Field(..., description="전체 여행 아키타입")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sentences": [
                    {
                        "index": 1,
                        "feel": "진짜 거기 풍경 보고 말문이 턱 막혔어요, 너무 예뻐서요.",
                        "tags": ["설렘", "위로", "감탄", "예쁨"]
                    },
                    {
                        "index": 2,
                        "feel": "그냥 걷기만 해도 힐링 되는 곳이었어요, 마음이 편안해졌어요.",
                        "tags": ["힐링", "편안함", "산책", "자연치유", "고요함"]
                    }
                ],
                "overall_archetype": "고요한 회복러"
            }
        }
