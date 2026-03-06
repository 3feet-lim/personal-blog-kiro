"""카테고리 스키마 모듈

카테고리 관련 Pydantic 스키마를 정의합니다.
생성, 응답, 트리 구조 스키마를 포함합니다.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """카테고리 생성 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="카테고리 이름")
    parent_id: int | None = Field(None, description="부모 카테고리 ID (없으면 최상위)")


class CategoryUpdate(BaseModel):
    """카테고리 수정 스키마"""
    name: str | None = Field(None, min_length=1, max_length=100, description="카테고리 이름")
    parent_id: int | None = Field(None, description="부모 카테고리 ID")


class CategoryResponse(BaseModel):
    """카테고리 응답 스키마"""
    id: int
    name: str
    slug: str
    parent_id: int | None
    order: int

    model_config = {"from_attributes": True}


class CategoryTree(BaseModel):
    """카테고리 트리 스키마 (재귀적 구조)"""
    id: int
    name: str
    slug: str
    children: list[CategoryTree] = []

    model_config = {"from_attributes": True}
