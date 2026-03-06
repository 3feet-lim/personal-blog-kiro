"""인증 의존성 모듈

FastAPI Depends()와 함께 사용하는 인증/인가 의존성 함수를 정의합니다.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole
from app.auth.service import AuthService
from app.common.exceptions import AuthenticationError, PermissionDeniedError
from app.database import get_db

# Bearer 토큰 추출 (auto_error=False로 선택적 인증 지원)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """현재 인증된 사용자를 반환하는 의존성

    Raises:
        AuthenticationError: 토큰이 없거나 유효하지 않은 경우
    """
    if credentials is None:
        raise AuthenticationError("인증 토큰이 필요합니다")

    auth_service = AuthService(db)
    payload = AuthService.verify_token(credentials.credentials, expected_type="access")
    return await auth_service.get_user_by_id(payload.user_id)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """선택적 인증 의존성 (인증 없이도 접근 가능한 엔드포인트용)

    토큰이 없으면 None을 반환하고, 토큰이 있으면 사용자를 반환합니다.
    """
    if credentials is None:
        return None

    try:
        auth_service = AuthService(db)
        payload = AuthService.verify_token(
            credentials.credentials, expected_type="access"
        )
        return await auth_service.get_user_by_id(payload.user_id)
    except Exception:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """관리자 권한을 요구하는 의존성

    Raises:
        PermissionDeniedError: 사용자가 관리자가 아닌 경우
    """
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedError("관리자 권한이 필요합니다")
    return current_user
