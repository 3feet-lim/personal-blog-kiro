"""인증 스키마 모듈

로그인, 토큰, 사용자 관련 Pydantic 스키마를 정의합니다.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.auth.models import UserRole


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserPayload(BaseModel):
    """JWT 토큰 페이로드에 포함되는 사용자 정보"""
    user_id: int
    email: str
    role: UserRole


class UserCreate(BaseModel):
    """사용자 생성 요청 스키마"""
    email: EmailStr
    password: str
    name: str
    role: UserRole = UserRole.FAMILY_MEMBER


class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    id: int
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
