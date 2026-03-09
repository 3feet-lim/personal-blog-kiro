"""포스트 리포지토리 모듈

포스트 데이터 접근 로직을 담당합니다.
SQLAlchemy async session을 사용하여 CRUD 작업을 수행합니다.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.posts.models import Post, Visibility
from app.tags.models import PostTag


class PostRepository:
    """포스트 데이터 접근 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post: Post) -> Post:
        """새 포스트를 저장합니다."""
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post, attribute_names=["author", "category", "post_tags"])
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        """ID로 포스트를 조회합니다 (author, category, post_tags 관계 포함)."""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.post_tags).selectinload(PostTag.tag),
            )
            .where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Post | None:
        """슬러그로 포스트를 조회합니다 (author, category, post_tags 관계 포함)."""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.post_tags).selectinload(PostTag.tag),
            )
            .where(Post.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        visibility: Visibility | None,
        category_id: int | None,
        offset: int,
        limit: int,
    ) -> list[Post]:
        """포스트 목록을 조회합니다.

        Args:
            visibility: 공개 범위 필터 (None이면 전체)
            category_id: 카테고리 필터 (None이면 전체)
            offset: 시작 위치
            limit: 조회 개수
        """
        query = (
            select(Post)
            .options(selectinload(Post.author), selectinload(Post.category))
        )

        if visibility is not None:
            query = query.where(Post.visibility == visibility)

        if category_id is not None:
            query = query.where(Post.category_id == category_id)

        query = query.order_by(Post.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        visibility: Visibility | None,
        category_id: int | None,
    ) -> int:
        """조건에 맞는 포스트 수를 조회합니다."""
        query = select(func.count(Post.id))

        if visibility is not None:
            query = query.where(Post.visibility == visibility)

        if category_id is not None:
            query = query.where(Post.category_id == category_id)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, post: Post) -> Post:
        """포스트를 업데이트합니다."""
        await self.db.flush()
        await self.db.refresh(post, attribute_names=["author", "category", "post_tags"])
        return post

    async def delete(self, post: Post) -> None:
        """포스트를 삭제합니다."""
        await self.db.delete(post)
        await self.db.flush()

    async def slug_exists(self, slug: str) -> bool:
        """슬러그가 이미 존재하는지 확인합니다."""
        result = await self.db.execute(
            select(func.count(Post.id)).where(Post.slug == slug)
        )
        return result.scalar_one() > 0
