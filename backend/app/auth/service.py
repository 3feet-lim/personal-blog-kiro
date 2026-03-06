"""인증 서비스 모듈

비밀번호 해싱, JWT 토큰 생성/검증, 로그인/토큰 갱신 로직을 담당합니다.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole
from app.auth.repository import UserRepository
from app.auth.schemas import TokenResponse, UserCreate, UserPayload
from app.common.exceptions import (
    AuthenticationError,
    DuplicateError,
    NotFoundError,
    TokenExpiredError,
)
from app.config import get_settings

settings = get_settings()

# bcrypt 기반 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """인증 비즈니스 로직을 처리하는 서비스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    # ── 비밀번호 해싱 ──

    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호를 bcrypt 해시로 변환합니다."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """평문 비밀번호와 해시를 비교합니다."""
        return pwd_context.verify(plain_password, hashed_password)

    # ── JWT 토큰 ──

    @staticmethod
    def create_access_token(payload: UserPayload) -> str:
        """액세스 토큰을 생성합니다."""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        to_encode = {
            "sub": str(payload.user_id),
            "email": payload.email,
            "role": payload.role.value,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(
            to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

    @staticmethod
    def create_refresh_token(payload: UserPayload) -> str:
        """리프레시 토큰을 생성합니다."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        to_encode = {
            "sub": str(payload.user_id),
            "email": payload.email,
            "role": payload.role.value,
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(
            to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> UserPayload:
        """토큰을 검증하고 사용자 정보를 추출합니다.

        Args:
            token: JWT 토큰 문자열
            expected_type: 기대하는 토큰 타입 ("access" 또는 "refresh")

        Returns:
            UserPayload: 토큰에 포함된 사용자 정보

        Raises:
            TokenExpiredError: 토큰이 만료된 경우
            AuthenticationError: 토큰이 유효하지 않은 경우
        """
        try:
            decoded = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
        except JWTError as e:
            # python-jose는 만료 시 ExpiredSignatureError를 발생시킴
            if "expired" in str(e).lower():
                raise TokenExpiredError()
            raise AuthenticationError("유효하지 않은 토큰입니다")

        # 토큰 타입 검증
        if decoded.get("type") != expected_type:
            raise AuthenticationError("유효하지 않은 토큰 타입입니다")

        return UserPayload(
            user_id=int(decoded["sub"]),
            email=decoded["email"],
            role=UserRole(decoded["role"]),
        )

    # ── 로그인 / 토큰 갱신 ──

    async def login(self, email: str, password: str) -> TokenResponse:
        """이메일과 비밀번호로 로그인하고 토큰을 발급합니다.

        Raises:
            AuthenticationError: 자격 증명이 유효하지 않은 경우
        """
        user = await self.user_repo.get_by_email(email)

        if user is None or not user.is_active:
            raise AuthenticationError("이메일 또는 비밀번호가 올바르지 않습니다")

        if user.password_hash is None or not self.verify_password(
            password, user.password_hash
        ):
            raise AuthenticationError("이메일 또는 비밀번호가 올바르지 않습니다")

        payload = UserPayload(
            user_id=user.id, email=user.email, role=UserRole(user.role)
        )
        return TokenResponse(
            access_token=self.create_access_token(payload),
            refresh_token=self.create_refresh_token(payload),
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """리프레시 토큰으로 새 토큰 쌍을 발급합니다.

        Raises:
            TokenExpiredError: 리프레시 토큰이 만료된 경우
            AuthenticationError: 리프레시 토큰이 유효하지 않은 경우
            NotFoundError: 사용자가 존재하지 않는 경우
        """
        payload = self.verify_token(refresh_token, expected_type="refresh")

        # DB에서 사용자 존재 및 활성 상태 확인
        user = await self.user_repo.get_by_id(payload.user_id)

        if user is None or not user.is_active:
            raise AuthenticationError("유효하지 않은 사용자입니다")

        new_payload = UserPayload(
            user_id=user.id, email=user.email, role=UserRole(user.role)
        )
        return TokenResponse(
            access_token=self.create_access_token(new_payload),
            refresh_token=self.create_refresh_token(new_payload),
        )

    # ── 사용자 관리 ──

    async def get_user_by_id(self, user_id: int) -> User:
        """ID로 사용자를 조회합니다.

        Raises:
            NotFoundError: 사용자가 존재하지 않는 경우
        """
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("사용자", str(user_id))
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """새 사용자를 생성합니다.

        이메일 고유성을 검증하고 비밀번호를 해싱하여 저장합니다.

        Raises:
            DuplicateError: 이메일이 이미 존재하는 경우
        """
        user = User(
            email=user_data.email,
            password_hash=self.hash_password(user_data.password),
            name=user_data.name,
            role=user_data.role,
        )
        return await self.user_repo.create(user)

    async def get_users(self) -> list[User]:
        """모든 사용자 목록을 조회합니다."""
        return await self.user_repo.get_all()

    async def deactivate_user(self, user_id: int) -> None:
        """사용자를 비활성화합니다.

        Raises:
            NotFoundError: 사용자가 존재하지 않는 경우
        """
        await self.user_repo.deactivate(user_id)
