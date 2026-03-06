"""공통 응답 스키마 모듈

API 응답의 일관된 형식을 정의합니다.
- ApiResponse: 단일 데이터 응답
- ErrorResponse: 오류 응답
- PaginatedResponse: 페이지네이션된 목록 응답
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """단일 데이터 성공 응답 스키마"""

    data: T
    message: str | None = None


class ErrorResponse(BaseModel):
    """오류 응답 스키마"""

    error: str
    message: str
    details: dict | None = None


class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""

    page: int
    size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션된 목록 응답 스키마"""

    data: list[T]
    pagination: PaginationMeta
