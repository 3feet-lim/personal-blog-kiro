"""포스트 스키마 모듈

포스트 관련 Pydantic 스키마를 정의합니다.
생성, 수정, 응답, 목록 아이템 스키마를 포함합니다.
"""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.auth.schemas import UserResponse
from app.categories.schemas import CategoryResponse
from app.posts.models import Visibility
from app.tags.schemas import TagResponse


class PostCreate(BaseModel):
    """포스트 생성 스키마"""
    title: str = Field(..., min_length=1, max_length=255, description="포스트 제목")
    content: str = Field(..., min_length=1, description="마크다운 형식의 포스트 내용")
    visibility: Visibility = Field(
        default=Visibility.PUBLIC, description="공개 범위 (public/private)"
    )
    category_id: int | None = Field(None, description="카테고리 ID")
    tag_ids: list[int] = Field(default_factory=list, description="태그 ID 목록")


class PostUpdate(BaseModel):
    """포스트 수정 스키마"""
    title: str | None = Field(None, min_length=1, max_length=255, description="포스트 제목")
    content: str | None = Field(None, min_length=1, description="마크다운 형식의 포스트 내용")
    visibility: Visibility | None = Field(None, description="공개 범위 (public/private)")
    category_id: int | None = Field(None, description="카테고리 ID")
    tag_ids: list[int] | None = Field(None, description="태그 ID 목록")


class PostResponse(BaseModel):
    """포스트 상세 응답 스키마"""
    id: int
    title: str
    slug: str
    content: str
    visibility: Visibility
    author: UserResponse
    category: CategoryResponse | None
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_tags(cls, data: object) -> object:
        """post_tags 관계에서 태그 목록을 추출합니다."""
        if hasattr(data, "post_tags") and not hasattr(data, "tags"):
            data.tags = [pt.tag for pt in data.post_tags if pt.tag]  # type: ignore[attr-defined]
        return data


class PostListItem(BaseModel):
    """포스트 목록 아이템 스키마"""
    id: int
    title: str
    slug: str
    visibility: Visibility
    author_name: str
    category_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
