"""인증 라우터 모듈

로그인, 토큰 갱신, 현재 사용자 조회 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import LoginRequest, TokenResponse, UserResponse
from app.auth.service import AuthService
from app.common.responses import ApiResponse
from app.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["인증"])


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """이메일/비밀번호로 로그인하여 토큰을 발급합니다."""
    auth_service = AuthService(db)
    tokens = await auth_service.login(body.email, body.password)
    return ApiResponse(data=tokens)


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """리프레시 토큰으로 새 토큰 쌍을 발급합니다."""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(refresh_token)
    return ApiResponse(data=tokens)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 인증된 사용자 정보를 반환합니다."""
    return ApiResponse(data=UserResponse.model_validate(current_user))
