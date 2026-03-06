"""카테고리 라우터 모듈

카테고리 CRUD 엔드포인트를 정의합니다.
- GET /api/v1/categories - 카테고리 트리 조회 (인증 불필요)
- POST /api/v1/categories - 카테고리 생성 (ADMIN 전용)
- PUT /api/v1/categories/{id} - 카테고리 수정 (ADMIN 전용)
- DELETE /api/v1/categories/{id} - 카테고리 삭제 (ADMIN 전용)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
)
from app.categories.service import CategoryService
from app.common.responses import ApiResponse
from app.database import get_db

router = APIRouter(prefix="/api/v1/categories", tags=["카테고리"])


@router.get("", response_model=ApiResponse[list[CategoryTree]])
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
):
    """카테고리 트리를 조회합니다. (인증 불필요)"""
    service = CategoryService(db)
    tree = await service.get_category_tree()
    return ApiResponse(data=tree)


@router.post(
    "",
    response_model=ApiResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    body: CategoryCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """새 카테고리를 생성합니다. (관리자 전용)"""
    service = CategoryService(db)
    category = await service.create_category(body)
    return ApiResponse(data=CategoryResponse.model_validate(category))


@router.put("/{category_id}", response_model=ApiResponse[CategoryResponse])
async def update_category(
    category_id: int,
    body: CategoryUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """카테고리를 수정합니다. (관리자 전용)"""
    service = CategoryService(db)
    category = await service.update_category(category_id, body)
    return ApiResponse(data=CategoryResponse.model_validate(category))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """카테고리를 삭제합니다. (관리자 전용)

    카테고리에 포스트가 존재하면 삭제가 거부됩니다.
    """
    service = CategoryService(db)
    await service.delete_category(category_id)
