"""태그 라우터 모듈

태그 CRUD 및 포스트-태그 관계 관리 엔드포인트를 정의합니다.
- POST /api/v1/tags - 태그 생성 (ADMIN 전용)
- PUT /api/v1/tags/{id} - 태그 수정 (ADMIN 전용)
- DELETE /api/v1/tags/{id} - 태그 삭제 (ADMIN 전용)
- GET /api/v1/tags - 태그 목록 조회 (인증 불필요)
- GET /api/v1/tags/{slug}/posts - 태그별 포스트 필터링 (선택적 인증)
- POST /api/v1/posts/{id}/tags - 포스트에 태그 할당 (ADMIN 전용)
- DELETE /api/v1/posts/{id}/tags/{tag_id} - 포스트에서 태그 제거 (ADMIN 전용)
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_optional_user, require_admin
from app.auth.models import User
from app.common.responses import ApiResponse, PaginatedResponse
from app.database import get_db
from app.posts.schemas import PostListItem
from app.tags.schemas import TagAssign, TagCreate, TagResponse, TagUpdate
from app.tags.service import TagService

# 태그 CRUD 라우터
router = APIRouter(prefix="/api/v1/tags", tags=["태그"])

# 포스트-태그 관계 라우터
post_tag_router = APIRouter(prefix="/api/v1/posts", tags=["포스트-태그"])


# ── 태그 CRUD 엔드포인트 ──


@router.get("", response_model=ApiResponse[list[TagResponse]])
async def get_tags(
    db: AsyncSession = Depends(get_db),
):
    """모든 태그 목록을 조회합니다. (인증 불필요)"""
    service = TagService(db)
    tags = await service.get_all_tags()
    return ApiResponse(
        data=[TagResponse.model_validate(tag) for tag in tags],
    )


@router.post(
    "",
    response_model=ApiResponse[TagResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    body: TagCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """새 태그를 생성합니다. (관리자 전용)"""
    service = TagService(db)
    tag = await service.create_tag(body)
    return ApiResponse(data=TagResponse.model_validate(tag))


@router.put("/{tag_id}", response_model=ApiResponse[TagResponse])
async def update_tag(
    tag_id: int,
    body: TagUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """태그를 수정합니다. (관리자 전용)"""
    service = TagService(db)
    tag = await service.update_tag(tag_id, body)
    return ApiResponse(data=TagResponse.model_validate(tag))


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """태그를 삭제합니다. (관리자 전용)

    cascade 설정으로 포스트-태그 관계도 함께 삭제됩니다.
    """
    service = TagService(db)
    await service.delete_tag(tag_id)


@router.get("/{slug}/posts", response_model=PaginatedResponse[PostListItem])
async def get_posts_by_tag(
    slug: str,
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """태그별 포스트 목록을 조회합니다. (선택적 인증)

    인증된 사용자는 모든 포스트를, 비인증 사용자는 PUBLIC 포스트만 볼 수 있습니다.
    """
    service = TagService(db)
    result = await service.get_posts_by_tag(slug, user, page, size)

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


# ── 포스트-태그 관계 엔드포인트 ──


@post_tag_router.post(
    "/{post_id}/tags",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
async def assign_tag_to_post(
    post_id: int,
    body: TagAssign,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """포스트에 태그를 할당합니다. (관리자 전용)"""
    service = TagService(db)
    await service.assign_tag_to_post(post_id, body.tag_id)
    return ApiResponse(data={"post_id": post_id, "tag_id": body.tag_id})


@post_tag_router.delete(
    "/{post_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_tag_from_post(
    post_id: int,
    tag_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """포스트에서 태그를 제거합니다. (관리자 전용)"""
    service = TagService(db)
    await service.remove_tag_from_post(post_id, tag_id)
