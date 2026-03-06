"""공통 유틸리티 모듈

응답 스키마, 커스텀 예외, 페이지네이션 유틸리티를 제공합니다.
"""

from app.common.exceptions import (
    AuthenticationError,
    BlogException,
    CategoryNotEmptyError,
    DuplicateError,
    ImageFormatError,
    NotFoundError,
    PermissionDeniedError,
    TokenExpiredError,
    ValidationError,
)
from app.common.pagination import paginate
from app.common.responses import (
    ApiResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
)

__all__ = [
    # 응답 스키마
    "ApiResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    # 예외 클래스
    "BlogException",
    "AuthenticationError",
    "TokenExpiredError",
    "PermissionDeniedError",
    "NotFoundError",
    "DuplicateError",
    "ValidationError",
    "ImageFormatError",
    "CategoryNotEmptyError",
    # 유틸리티
    "paginate",
]
