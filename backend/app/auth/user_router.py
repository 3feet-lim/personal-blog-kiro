"""사용자 관리 라우터 모듈

관리자 전용 사용자 목록 조회, 생성, 비활성화 엔드포인트를 정의합니다.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.auth.schemas import UserCreate, UserResponse
from app.auth.service import AuthService
from app.common.responses import ApiResponse
from app.database import get_db

router = APIRouter(prefix="/api/v1/users", tags=["사용자 관리"])


@router.get("", response_model=ApiResponse[list[UserResponse]])
async def get_users(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """모든 사용자 목록을 조회합니다. (관리자 전용)"""
    auth_service = AuthService(db)
    users = await auth_service.get_users()
    return ApiResponse(
        data=[UserResponse.model_validate(u) for u in users],
    )


@router.post(
    "",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    body: UserCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """새 사용자를 생성합니다. (관리자 전용)"""
    auth_service = AuthService(db)
    user = await auth_service.create_user(body)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """사용자를 비활성화합니다. (관리자 전용)"""
    auth_service = AuthService(db)
    await auth_service.deactivate_user(user_id)
