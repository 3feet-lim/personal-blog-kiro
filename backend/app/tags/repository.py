"""태그 리포지토리 모듈

태그 데이터 접근 로직을 담당합니다.
SQLAlchemy async session을 사용하여 CRUD 작업을 수행합니다.
포스트-태그 다대다 관계 관리를 포함합니다.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.posts.models import Post, Visibility
from app.tags.models import Tag, PostTag


class TagRepository:
    """태그 데이터 접근 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── 태그 CRUD ──

    async def create(self, tag: Tag) -> Tag:
        """새 태그를 저장합니다."""
        self.db.add(tag)
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def get_by_id(self, tag_id: int) -> Tag | None:
        """ID로 태그를 조회합니다."""
        result = await self.db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Tag | None:
        """이름으로 태그를 조회합니다."""
        result = await self.db.execute(
            select(Tag).where(Tag.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Tag | None:
        """슬러그로 태그를 조회합니다."""
        result = await self.db.execute(
            select(Tag).where(Tag.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Tag]:
        """모든 태그를 이름순으로 조회합니다."""
        result = await self.db.execute(
            select(Tag).order_by(Tag.name)
        )
        return list(result.scalars().all())

    async def update(self, tag: Tag) -> Tag:
        """태그를 업데이트합니다."""
        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def delete(self, tag: Tag) -> None:
        """태그를 삭제합니다.

        cascade 설정으로 관련 PostTag도 함께 삭제됩니다.
        """
        await self.db.delete(tag)
        await self.db.flush()

    async def name_exists(self, name: str, exclude_id: int | None = None) -> bool:
        """태그 이름이 이미 존재하는지 확인합니다.

        Args:
            name: 확인할 태그 이름
            exclude_id: 제외할 태그 ID (수정 시 자기 자신 제외)
        """
        query = select(func.count(Tag.id)).where(Tag.name == name)
        if exclude_id is not None:
            query = query.where(Tag.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one() > 0

    async def slug_exists(self, slug: str) -> bool:
        """슬러그가 이미 존재하는지 확인합니다."""
        result = await self.db.execute(
            select(func.count(Tag.id)).where(Tag.slug == slug)
        )
        return result.scalar_one() > 0

    # ── 포스트-태그 관계 관리 ──

    async def assign_tag_to_post(self, post_id: int, tag_id: int) -> PostTag:
        """포스트에 태그를 할당합니다.

        이미 할당된 경우 기존 관계를 반환합니다.
        """
        # 이미 할당되어 있는지 확인
        existing = await self._get_post_tag(post_id, tag_id)
        if existing is not None:
            return existing

        post_tag = PostTag(post_id=post_id, tag_id=tag_id)
        self.db.add(post_tag)
        await self.db.flush()
        await self.db.refresh(post_tag)
        return post_tag

    async def remove_tag_from_post(self, post_id: int, tag_id: int) -> None:
        """포스트에서 태그를 제거합니다."""
        post_tag = await self._get_post_tag(post_id, tag_id)
        if post_tag is not None:
            await self.db.delete(post_tag)
            await self.db.flush()

    async def _get_post_tag(self, post_id: int, tag_id: int) -> PostTag | None:
        """포스트-태그 관계를 조회합니다."""
        result = await self.db.execute(
            select(PostTag).where(
                PostTag.post_id == post_id,
                PostTag.tag_id == tag_id,
            )
        )
        return result.scalar_one_or_none()

    # ── 태그별 포스트 조회 ──

    async def get_posts_by_tag(
        self,
        tag_id: int,
        visibility: Visibility | None,
        offset: int,
        limit: int,
    ) -> list[Post]:
        """태그에 할당된 포스트 목록을 조회합니다.

        Args:
            tag_id: 태그 ID
            visibility: 공개 범위 필터 (None이면 전체)
            offset: 시작 위치
            limit: 조회 개수
        """
        query = (
            select(Post)
            .join(PostTag, PostTag.post_id == Post.id)
            .options(selectinload(Post.author), selectinload(Post.category))
            .where(PostTag.tag_id == tag_id)
        )

        if visibility is not None:
            query = query.where(Post.visibility == visibility)

        query = query.order_by(Post.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_posts_by_tag(
        self,
        tag_id: int,
        visibility: Visibility | None,
    ) -> int:
        """태그에 할당된 포스트 수를 조회합니다."""
        query = (
            select(func.count(Post.id))
            .join(PostTag, PostTag.post_id == Post.id)
            .where(PostTag.tag_id == tag_id)
        )

        if visibility is not None:
            query = query.where(Post.visibility == visibility)

        result = await self.db.execute(query)
        return result.scalar_one()
