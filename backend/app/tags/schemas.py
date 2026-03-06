"""태그 스키마 모듈

태그 관련 Pydantic 스키마를 정의합니다.
생성, 수정, 응답 스키마를 포함합니다.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """태그 생성 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="태그 이름")


class TagUpdate(BaseModel):
    """태그 수정 스키마"""
    name: str | None = Field(None, min_length=1, max_length=100, description="태그 이름")


class TagAssign(BaseModel):
    """포스트에 태그 할당 시 사용하는 스키마"""
    tag_id: int = Field(..., description="할당할 태그 ID")


class TagResponse(BaseModel):
    """태그 응답 스키마"""
    id: int
    name: str
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}
