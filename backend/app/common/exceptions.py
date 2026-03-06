"""커스텀 예외 클래스 모듈

블로그 시스템에서 사용하는 도메인 예외를 정의합니다.
각 예외는 고유한 에러 코드를 가지며, 전역 예외 핸들러에서
적절한 HTTP 상태 코드로 변환됩니다.
"""


class BlogException(Exception):
    """블로그 시스템 기본 예외"""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(BlogException):
    """인증 실패 예외"""

    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(message, "AUTH_FAILED")


class TokenExpiredError(BlogException):
    """토큰 만료 예외"""

    def __init__(self, message: str = "토큰이 만료되었습니다"):
        super().__init__(message, "TOKEN_EXPIRED")


class PermissionDeniedError(BlogException):
    """권한 부족 예외"""

    def __init__(self, message: str = "권한이 없습니다"):
        super().__init__(message, "PERMISSION_DENIED")


class NotFoundError(BlogException):
    """리소스 없음 예외"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource}을(를) 찾을 수 없습니다: {identifier}", "NOT_FOUND"
        )


class DuplicateError(BlogException):
    """중복 데이터 예외"""

    def __init__(self, field: str, value: str):
        super().__init__(f"이미 존재하는 {field}입니다: {value}", "DUPLICATE")


class ValidationError(BlogException):
    """유효성 검사 예외"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.details = details


class ImageFormatError(BlogException):
    """이미지 형식 오류 예외"""

    def __init__(self, format: str):
        super().__init__(
            f"지원하지 않는 이미지 형식입니다: {format}", "INVALID_IMAGE_FORMAT"
        )


class CategoryNotEmptyError(BlogException):
    """카테고리에 포스트 존재 예외"""

    def __init__(self, category_id: int):
        super().__init__(
            f"카테고리에 포스트가 존재하여 삭제할 수 없습니다: {category_id}",
            "CATEGORY_NOT_EMPTY",
        )
