"""카테고리 리포지토리 모듈

카테고리 데이터 접근 로직을 담당합니다.
SQLAlchemy async session을 사용하여 CRUD 작업을 수행합니다.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.categories.models import Category
from app.common.exceptions import DuplicateError, NotFoundError


class CategoryRepository:
    """카테고리 데이터 접근 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        """ID로 카테고리를 조회합니다."""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        """슬러그로 카테고리를 조회합니다."""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        """모든 카테고리를 정렬하여 조회합니다."""
        result = await self.db.execute(
            select(Category).order_by(Category.order, Category.id)
        )
        return list(result.scalars().all())

    async def create(self, category: Category) -> Category:
        """새 카테고리를 저장합니다.

        슬러그 고유성을 검증한 후 카테고리를 생성합니다.

        Raises:
            DuplicateError: 슬러그가 이미 존재하는 경우
        """
        existing = await self.get_by_slug(category.slug)
        if existing is not None:
            raise DuplicateError("슬러그", category.slug)

        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def update(self, category: Category) -> Category:
        """카테고리를 업데이트합니다."""
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        """카테고리를 삭제합니다."""
        await self.db.delete(category)
        await self.db.flush()

    async def count_posts_in_category(self, category_id: int) -> int:
        """카테고리에 속한 포스트 수를 조회합니다.

        Post 모델이 아직 없는 경우를 대비하여
        동적으로 테이블 존재 여부를 확인합니다.
        """
        try:
            from app.posts.models import Post
            result = await self.db.execute(
                select(func.count(Post.id)).where(
                    Post.category_id == category_id
                )
            )
            return result.scalar_one()
        except Exception:
            # Post 모델이 아직 없는 경우 0 반환
            return 0

    async def get_descendant_ids(self, category_id: int) -> list[int]:
        """카테고리의 모든 하위 카테고리 ID를 재귀적으로 조회합니다."""
        all_categories = await self.get_all()
        descendants = []
        self._collect_descendants(category_id, all_categories, descendants)
        return descendants

    def _collect_descendants(
        self,
        parent_id: int,
        all_categories: list[Category],
        result: list[int],
    ) -> None:
        """재귀적으로 하위 카테고리 ID를 수집합니다."""
        for cat in all_categories:
            if cat.parent_id == parent_id:
                result.append(cat.id)
                self._collect_descendants(cat.id, all_categories, result)

    async def slug_exists(self, slug: str) -> bool:
        """슬러그가 이미 존재하는지 확인합니다."""
        result = await self.db.execute(
            select(func.count(Category.id)).where(Category.slug == slug)
        )
        return result.scalar_one() > 0
