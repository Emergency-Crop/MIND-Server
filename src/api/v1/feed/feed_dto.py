"""
Feed DTO Module

사용자 아키타입 기반 피드 조회 API의 요청/응답 스키마 정의
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class FeedRequestDTO(BaseModel):
    """피드 조회 요청 DTO"""
    user_id: UUID = Field(..., description="사용자 ID (UUID)")
    limit: int = Field(default=20, ge=1, le=50, description="반환할 최대 결과 수")
    cursor: Optional[str] = Field(None, description="다음 페이지 커서 (Base64 인코딩)")

    @field_validator('user_id')
    def validate_user_id(cls, v):
        if not v:
            raise ValueError("사용자 ID는 필수입니다.")
        return v


class TravelLogItemDTO(BaseModel):
    """여행 로그 항목 DTO"""
    id: UUID = Field(..., description="여행 로그 ID")
    created_at: datetime = Field(..., description="생성 시간")


class UserProfileDTO(BaseModel):
    """사용자 프로필 DTO"""
    id: UUID = Field(..., description="사용자 ID")
    archetype: str = Field(..., description="사용자 아키타입")
    display_name: str = Field(..., description="사용자 표시명")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    bio: Optional[str] = Field(None, description="사용자 소개")


class FeedMetaDTO(BaseModel):
    """피드 메타 정보 DTO"""
    user_profile: UserProfileDTO = Field(..., description="요청한 사용자 프로필")
    total_count: int = Field(..., description="총 결과 수")
    current_count: int = Field(..., description="현재 페이지 결과 수")
    limit: int = Field(..., description="페이지당 결과 수")
    has_more: bool = Field(..., description="더 많은 결과가 있는지 여부")
    next_cursor: Optional[str] = Field(None, description="다음 페이지 커서 (Base64 인코딩)")


class FeedResponseDTO(BaseModel):
    """피드 조회 응답 DTO"""
    meta: FeedMetaDTO = Field(..., description="피드 메타 정보")
    items: List[TravelLogItemDTO] = Field(..., description="여행 로그 목록")
