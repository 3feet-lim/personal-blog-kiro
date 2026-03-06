"""포스트 라우터 모듈

포스트 CRUD 및 목록 조회 엔드포인트를 정의합니다.
- GET /api/v1/posts - 포스트 목록 (선택적 인증, 페이지네이션, 카테고리 필터)
- GET /api/v1/posts/{slug} - 포스트 상세 (선택적 인증)
- POST /api/v1/posts - 포스트 생성 (ADMIN 전용)
- PUT /api/v1/posts/{id} - 포스트 수정 (ADMIN 전용)
- DELETE /api/v1/posts/{id} - 포스트 삭제 (ADMIN 전용)
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_optional_user, require_admin
from app.auth.models import User
from app.common.responses import ApiResponse, PaginatedResponse
from app.database import get_db
from app.posts.schemas import (
    PostCreate,
    PostListItem,
    PostResponse,
    PostUpdate,
)
from app.posts.service import PostService

router = APIRouter(prefix="/api/v1/posts", tags=["포스트"])


@router.get("", response_model=PaginatedResponse[PostListItem])
async def get_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    category_id: int | None = Query(None, description="카테고리 필터"),
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """포스트 목록을 조회합니다. (선택적 인증)

    인증된 사용자는 모든 포스트를, 비인증 사용자는 PUBLIC 포스트만 볼 수 있습니다.
    """
    service = PostService(db)
    result = await service.get_posts(user, category_id, page, size)

    # PostListItem으로 변환
    items = [
        PostListItem(
            id=post.id,
            title=post.title,
            slug=post.slug,
            visibility=post.visibility,
            author_name=post.author.name,
            category_name=post.category.name if post.category else None,
            created_at=post.created_at,
        )
        for post in result.data
    ]

    return PaginatedResponse(data=items, pagination=result.pagination)


@router.get("/{slug}", response_model=ApiResponse[PostResponse])
async def get_post_by_slug(
    slug: str,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """슬러그로 포스트를 조회합니다. (선택적 인증)

    비인증 사용자가 PRIVATE 포스트에 접근하면 403 에러를 반환합니다.
    """
    service = PostService(db)
    post = await service.get_post_by_slug(slug, user)
    return ApiResponse(data=PostResponse.model_validate(post))


@router.post(
    "",
    response_model=ApiResponse[PostResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    body: PostCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """새 포스트를 생성합니다. (관리자 전용)"""
    service = PostService(db)
    post = await service.create_post(body, admin.id)
    return ApiResponse(data=PostResponse.model_validate(post))


@router.put("/{post_id}", response_model=ApiResponse[PostResponse])
async def update_post(
    post_id: int,
    body: PostUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """포스트를 수정합니다. (관리자 전용)"""
    service = PostService(db)
    post = await service.update_post(post_id, body)
    return ApiResponse(data=PostResponse.model_validate(post))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """포스트를 삭제합니다. (관리자 전용)"""
    service = PostService(db)
    await service.delete_post(post_id)
