"""인증 서비스 단위 테스트

비밀번호 해싱, JWT 토큰 생성/검증, 인증 실패 처리 등을 검증합니다.
DB 의존성 없이 테스트 가능한 정적 메서드를 중심으로 테스트합니다.
"""

import time

import pytest
from jose import jwt

from app.auth.models import UserRole
from app.auth.schemas import UserPayload
from app.auth.service import AuthService
from app.common.exceptions import AuthenticationError, TokenExpiredError
from app.config import get_settings

settings = get_settings()


class TestPasswordHashing:
    """비밀번호 해싱 관련 테스트"""

    def test_hash_password_returns_bcrypt_hash(self):
        """해싱된 비밀번호는 bcrypt 형식이어야 한다 (Req 1.6)"""
        password = "test-password-123"
        hashed = AuthService.hash_password(password)
        # bcrypt 해시는 $2b$ 또는 $2a$로 시작
        assert hashed.startswith(("$2b$", "$2a$"))

    def test_verify_password_correct(self):
        """올바른 비밀번호로 검증 시 True를 반환해야 한다 (Req 1.6)"""
        password = "my-secure-password"
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """잘못된 비밀번호로 검증 시 False를 반환해야 한다 (Req 1.6)"""
        password = "my-secure-password"
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password("wrong-password", hashed) is False

    def test_hash_password_different_each_time(self):
        """동일한 비밀번호라도 매번 다른 해시를 생성해야 한다 (salt)"""
        password = "same-password"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        assert hash1 != hash2
        # 둘 다 원본 비밀번호로 검증 가능해야 함
        assert AuthService.verify_password(password, hash1) is True
        assert AuthService.verify_password(password, hash2) is True


class TestJWTToken:
    """JWT 토큰 생성/검증 관련 테스트"""

    @pytest.fixture
    def sample_payload(self) -> UserPayload:
        """테스트용 사용자 페이로드"""
        return UserPayload(
            user_id=1,
            email="admin@example.com",
            role=UserRole.ADMIN,
        )

    def test_create_access_token_contains_user_info(self, sample_payload):
        """액세스 토큰에 사용자 ID와 역할 정보가 포함되어야 한다 (Req 1.7)"""
        token = AuthService.create_access_token(sample_payload)
        decoded = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert decoded["sub"] == str(sample_payload.user_id)
        assert decoded["email"] == sample_payload.email
        assert decoded["role"] == sample_payload.role.value
        assert decoded["type"] == "access"

    def test_create_refresh_token_contains_user_info(self, sample_payload):
        """리프레시 토큰에 사용자 ID와 역할 정보가 포함되어야 한다 (Req 1.7)"""
        token = AuthService.create_refresh_token(sample_payload)
        decoded = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert decoded["sub"] == str(sample_payload.user_id)
        assert decoded["email"] == sample_payload.email
        assert decoded["role"] == sample_payload.role.value
        assert decoded["type"] == "refresh"

    def test_verify_access_token_roundtrip(self, sample_payload):
        """액세스 토큰 생성 후 검증하면 동일한 사용자 정보를 반환해야 한다 (Req 1.3)"""
        token = AuthService.create_access_token(sample_payload)
        result = AuthService.verify_token(token, expected_type="access")
        assert result.user_id == sample_payload.user_id
        assert result.email == sample_payload.email
        assert result.role == sample_payload.role

    def test_verify_refresh_token_roundtrip(self, sample_payload):
        """리프레시 토큰 생성 후 검증하면 동일한 사용자 정보를 반환해야 한다 (Req 1.5)"""
        token = AuthService.create_refresh_token(sample_payload)
        result = AuthService.verify_token(token, expected_type="refresh")
        assert result.user_id == sample_payload.user_id
        assert result.email == sample_payload.email
        assert result.role == sample_payload.role

    def test_verify_token_wrong_type_raises_error(self, sample_payload):
        """액세스 토큰을 리프레시 타입으로 검증하면 오류가 발생해야 한다"""
        token = AuthService.create_access_token(sample_payload)
        with pytest.raises(AuthenticationError, match="유효하지 않은 토큰 타입"):
            AuthService.verify_token(token, expected_type="refresh")

    def test_verify_invalid_token_raises_error(self):
        """유효하지 않은 토큰은 인증 오류를 발생시켜야 한다 (Req 1.2)"""
        with pytest.raises(AuthenticationError):
            AuthService.verify_token("invalid.token.string")

    def test_verify_expired_token_raises_error(self, sample_payload):
        """만료된 토큰은 TokenExpiredError를 발생시켜야 한다 (Req 1.4)"""
        # 이미 만료된 토큰 직접 생성
        from datetime import datetime, timedelta, timezone

        expire = datetime.now(timezone.utc) - timedelta(seconds=10)
        to_encode = {
            "sub": str(sample_payload.user_id),
            "email": sample_payload.email,
            "role": sample_payload.role.value,
            "exp": expire,
            "type": "access",
        }
        expired_token = jwt.encode(
            to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
        with pytest.raises((TokenExpiredError, AuthenticationError)):
            AuthService.verify_token(expired_token)

    def test_access_token_has_expiration(self, sample_payload):
        """액세스 토큰에 만료 시간이 설정되어야 한다"""
        token = AuthService.create_access_token(sample_payload)
        decoded = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "exp" in decoded

    def test_different_roles_in_token(self):
        """다른 역할의 사용자도 올바르게 토큰에 인코딩되어야 한다"""
        family_payload = UserPayload(
            user_id=2,
            email="family@example.com",
            role=UserRole.FAMILY_MEMBER,
        )
        token = AuthService.create_access_token(family_payload)
        result = AuthService.verify_token(token, expected_type="access")
        assert result.role == UserRole.FAMILY_MEMBER


class TestSchemas:
    """인증 스키마 관련 테스트"""

    def test_login_request_validates_email(self):
        """LoginRequest는 유효한 이메일 형식을 요구해야 한다"""
        from app.auth.schemas import LoginRequest

        # 유효한 이메일
        req = LoginRequest(email="user@example.com", password="pass")
        assert req.email == "user@example.com"

        # 유효하지 않은 이메일
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="pass")

    def test_user_create_default_role(self):
        """UserCreate의 기본 역할은 FAMILY_MEMBER여야 한다"""
        from app.auth.schemas import UserCreate

        user = UserCreate(
            email="new@example.com",
            password="password123",
            name="테스트 사용자",
        )
        assert user.role == UserRole.FAMILY_MEMBER

    def test_token_response_default_type(self):
        """TokenResponse의 기본 token_type은 'bearer'여야 한다"""
        from app.auth.schemas import TokenResponse

        resp = TokenResponse(
            access_token="access",
            refresh_token="refresh",
        )
        assert resp.token_type == "bearer"
