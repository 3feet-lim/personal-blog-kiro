"""커스텀 예외 클래스 단위 테스트"""

import pytest

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


class TestBlogException:
    """BlogException 기본 예외 테스트"""

    def test_message_and_error_code(self):
        exc = BlogException("테스트 오류", "TEST_ERROR")
        assert exc.message == "테스트 오류"
        assert exc.error_code == "TEST_ERROR"
        assert str(exc) == "테스트 오류"

    def test_is_exception(self):
        exc = BlogException("msg", "CODE")
        assert isinstance(exc, Exception)


class TestAuthenticationError:
    def test_default_message(self):
        exc = AuthenticationError()
        assert exc.error_code == "AUTH_FAILED"
        assert "인증" in exc.message

    def test_custom_message(self):
        exc = AuthenticationError("커스텀 인증 오류")
        assert exc.message == "커스텀 인증 오류"
        assert exc.error_code == "AUTH_FAILED"


class TestTokenExpiredError:
    def test_default_message(self):
        exc = TokenExpiredError()
        assert exc.error_code == "TOKEN_EXPIRED"
        assert "만료" in exc.message


class TestPermissionDeniedError:
    def test_default_message(self):
        exc = PermissionDeniedError()
        assert exc.error_code == "PERMISSION_DENIED"
        assert "권한" in exc.message


class TestNotFoundError:
    def test_message_format(self):
        exc = NotFoundError("포스트", "123")
        assert exc.error_code == "NOT_FOUND"
        assert "포스트" in exc.message
        assert "123" in exc.message


class TestDuplicateError:
    def test_message_format(self):
        exc = DuplicateError("이메일", "test@example.com")
        assert exc.error_code == "DUPLICATE"
        assert "이메일" in exc.message
        assert "test@example.com" in exc.message


class TestValidationError:
    def test_with_details(self):
        details = {"field": "title", "reason": "필수 항목"}
        exc = ValidationError("유효성 검사 실패", details=details)
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details == details

    def test_without_details(self):
        exc = ValidationError("유효성 검사 실패")
        assert exc.details is None


class TestImageFormatError:
    def test_message_format(self):
        exc = ImageFormatError("bmp")
        assert exc.error_code == "INVALID_IMAGE_FORMAT"
        assert "bmp" in exc.message


class TestCategoryNotEmptyError:
    def test_message_format(self):
        exc = CategoryNotEmptyError(42)
        assert exc.error_code == "CATEGORY_NOT_EMPTY"
        assert "42" in exc.message


class TestExceptionInheritance:
    """모든 커스텀 예외가 BlogException을 상속하는지 확인"""

    @pytest.mark.parametrize(
        "exc_class,args",
        [
            (AuthenticationError, ()),
            (TokenExpiredError, ()),
            (PermissionDeniedError, ()),
            (NotFoundError, ("리소스", "1")),
            (DuplicateError, ("필드", "값")),
            (ValidationError, ("메시지",)),
            (ImageFormatError, ("bmp",)),
            (CategoryNotEmptyError, (1,)),
        ],
    )
    def test_inherits_blog_exception(self, exc_class, args):
        exc = exc_class(*args)
        assert isinstance(exc, BlogException)
