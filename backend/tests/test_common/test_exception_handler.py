"""전역 예외 핸들러 통합 테스트

FastAPI 앱에 등록된 BlogException 핸들러가
올바른 HTTP 상태 코드와 응답 형식을 반환하는지 검증합니다.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.common.exceptions import (
    AuthenticationError,
    CategoryNotEmptyError,
    DuplicateError,
    ImageFormatError,
    NotFoundError,
    PermissionDeniedError,
    TokenExpiredError,
    ValidationError,
)
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """테스트용 비동기 HTTP 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# 테스트용 임시 라우트 등록
@app.get("/test/auth-error")
async def raise_auth_error():
    raise AuthenticationError()


@app.get("/test/token-expired")
async def raise_token_expired():
    raise TokenExpiredError()


@app.get("/test/permission-denied")
async def raise_permission_denied():
    raise PermissionDeniedError()


@app.get("/test/not-found")
async def raise_not_found():
    raise NotFoundError("포스트", "999")


@app.get("/test/duplicate")
async def raise_duplicate():
    raise DuplicateError("이메일", "test@example.com")


@app.get("/test/validation-error")
async def raise_validation_error():
    raise ValidationError("유효하지 않은 입력", details={"field": "title"})


@app.get("/test/image-format")
async def raise_image_format():
    raise ImageFormatError("bmp")


@app.get("/test/category-not-empty")
async def raise_category_not_empty():
    raise CategoryNotEmptyError(42)


@pytest.mark.anyio
class TestBlogExceptionHandler:
    """전역 예외 핸들러 테스트"""

    async def test_auth_error_returns_401(self, client):
        resp = await client.get("/test/auth-error")
        assert resp.status_code == 401
        body = resp.json()
        assert body["error"] == "AUTH_FAILED"
        assert "message" in body

    async def test_token_expired_returns_401(self, client):
        resp = await client.get("/test/token-expired")
        assert resp.status_code == 401
        assert resp.json()["error"] == "TOKEN_EXPIRED"

    async def test_permission_denied_returns_403(self, client):
        resp = await client.get("/test/permission-denied")
        assert resp.status_code == 403
        assert resp.json()["error"] == "PERMISSION_DENIED"

    async def test_not_found_returns_404(self, client):
        resp = await client.get("/test/not-found")
        assert resp.status_code == 404
        assert resp.json()["error"] == "NOT_FOUND"

    async def test_duplicate_returns_409(self, client):
        resp = await client.get("/test/duplicate")
        assert resp.status_code == 409
        assert resp.json()["error"] == "DUPLICATE"

    async def test_validation_error_returns_400_with_details(self, client):
        resp = await client.get("/test/validation-error")
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"] == "VALIDATION_ERROR"
        assert body["details"] == {"field": "title"}

    async def test_image_format_returns_400(self, client):
        resp = await client.get("/test/image-format")
        assert resp.status_code == 400
        assert resp.json()["error"] == "INVALID_IMAGE_FORMAT"

    async def test_category_not_empty_returns_409(self, client):
        resp = await client.get("/test/category-not-empty")
        assert resp.status_code == 409
        assert resp.json()["error"] == "CATEGORY_NOT_EMPTY"

    async def test_error_response_format(self, client):
        """오류 응답에 error, message 필드 포함 확인 (요구사항 7.2)"""
        resp = await client.get("/test/not-found")
        body = resp.json()
        assert "error" in body
        assert "message" in body
        assert "details" in body
