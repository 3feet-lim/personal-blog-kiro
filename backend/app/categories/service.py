"""카테고리 서비스 모듈

카테고리 생성, 트리 조회, 삭제 등 비즈니스 로직을 담당합니다.
슬러그 자동 생성 및 포스트 존재 시 삭제 거부 로직을 포함합니다.
"""

import re
import unicodedata

from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.models import Category
from app.categories.repository import CategoryRepository
from app.categories.schemas import CategoryCreate, CategoryUpdate, CategoryTree
from app.common.exceptions import (
    CategoryNotEmptyError,
    NotFoundError,
)


def generate_slug(name: str) -> str:
    """카테고리 이름에서 URL-safe 슬러그를 생성합니다.

    한글, 영문, 숫자를 지원합니다.
    - 영문/숫자: 소문자로 변환하여 유지
    - 한글: 그대로 유지
    - 공백 및 특수문자: 하이픈(-)으로 변환
    - 연속 하이픈 제거, 앞뒤 하이픈 제거
    """
    # 유니코드 정규화 (NFC)
    text = unicodedata.normalize("NFC", name.strip())

    # 소문자 변환
    text = text.lower()

    # 한글, 영문, 숫자, 공백, 하이픈만 유지
    text = re.sub(r"[^\w\s가-힣-]", "", text)

    # 공백 및 언더스코어를 하이픈으로 변환
    text = re.sub(r"[\s_]+", "-", text)

    # 연속 하이픈 제거
    text = re.sub(r"-+", "-", text)

    # 앞뒤 하이픈 제거
    text = text.strip("-")

    # 빈 문자열인 경우 기본값
    if not text:
        text = "category"

    return text


class CategoryService:
    """카테고리 비즈니스 로직을 처리하는 서비스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(db)

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """새 카테고리를 생성합니다.

        이름에서 슬러그를 자동 생성하고, 부모 카테고리가 지정된 경우
        존재 여부를 검증합니다.

        Args:
            category_data: 카테고리 생성 데이터

        Returns:
            생성된 Category 객체

        Raises:
            NotFoundError: 부모 카테고리가 존재하지 않는 경우
            DuplicateError: 슬러그가 이미 존재하는 경우
        """
        # 부모 카테고리 존재 여부 검증
        if category_data.parent_id is not None:
            parent = await self.repo.get_by_id(category_data.parent_id)
            if parent is None:
                raise NotFoundError("카테고리", str(category_data.parent_id))

        # 슬러그 자동 생성 (고유성 보장)
        base_slug = generate_slug(category_data.name)
        slug = await self._ensure_unique_slug(base_slug)

        category = Category(
            name=category_data.name,
            slug=slug,
            parent_id=category_data.parent_id,
        )
        return await self.repo.create(category)

    async def update_category(self, category_id: int, update_data: CategoryUpdate) -> Category:
        """카테고리를 수정합니다.

        이름 변경 시 슬러그를 재생성합니다.
        부모 카테고리 변경 시 존재 여부를 검증합니다.

        Args:
            category_id: 수정할 카테고리 ID
            update_data: 수정할 데이터

        Returns:
            수정된 Category 객체

        Raises:
            NotFoundError: 카테고리 또는 부모 카테고리가 존재하지 않는 경우
        """
        category = await self.repo.get_by_id(category_id)
        if category is None:
            raise NotFoundError("카테고리", str(category_id))

        # 이름 변경 시 슬러그 재생성
        if update_data.name is not None:
            category.name = update_data.name
            base_slug = generate_slug(update_data.name)
            # 현재 슬러그와 다른 경우에만 고유성 검증
            if base_slug != category.slug:
                category.slug = await self._ensure_unique_slug(base_slug)

        # 부모 카테고리 변경
        if update_data.parent_id is not None:
            parent = await self.repo.get_by_id(update_data.parent_id)
            if parent is None:
                raise NotFoundError("카테고리", str(update_data.parent_id))
            category.parent_id = update_data.parent_id

        return await self.repo.update(category)

    async def get_category_tree(self) -> list[CategoryTree]:
        """계층 구조 카테고리 트리를 조회합니다.

        모든 카테고리를 조회한 후 메모리에서 트리 구조로 변환합니다.
        최상위 카테고리(parent_id가 None)를 루트로 하여 재귀적으로 구성합니다.

        Returns:
            최상위 카테고리 트리 목록
        """
        all_categories = await self.repo.get_all()
        return self._build_tree(all_categories)

    async def delete_category(self, category_id: int) -> None:
        """카테고리를 삭제합니다.

        해당 카테고리 및 모든 하위 카테고리에 포스트가 존재하면
        삭제를 거부합니다. 포스트가 없으면 카테고리와 하위 카테고리를
        모두 삭제합니다 (cascade).

        Args:
            category_id: 삭제할 카테고리 ID

        Raises:
            NotFoundError: 카테고리가 존재하지 않는 경우
            CategoryNotEmptyError: 카테고리에 포스트가 존재하는 경우
        """
        category = await self.repo.get_by_id(category_id)
        if category is None:
            raise NotFoundError("카테고리", str(category_id))

        # 해당 카테고리 및 하위 카테고리의 포스트 존재 여부 확인
        await self._check_posts_exist(category_id)

        # cascade 옵션으로 하위 카테고리도 함께 삭제됨
        await self.repo.delete(category)

    async def _check_posts_exist(self, category_id: int) -> None:
        """카테고리 및 하위 카테고리에 포스트가 존재하는지 확인합니다.

        Raises:
            CategoryNotEmptyError: 포스트가 존재하는 경우
        """
        # 해당 카테고리의 포스트 확인
        post_count = await self.repo.count_posts_in_category(category_id)
        if post_count > 0:
            raise CategoryNotEmptyError(category_id)

        # 하위 카테고리의 포스트 확인
        descendant_ids = await self.repo.get_descendant_ids(category_id)
        for desc_id in descendant_ids:
            post_count = await self.repo.count_posts_in_category(desc_id)
            if post_count > 0:
                raise CategoryNotEmptyError(category_id)

    async def _ensure_unique_slug(self, base_slug: str) -> str:
        """슬러그의 고유성을 보장합니다.

        동일한 슬러그가 존재하면 숫자 접미사를 추가합니다.
        예: "tech" -> "tech-1" -> "tech-2"
        """
        slug = base_slug
        counter = 1

        while await self.repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @staticmethod
    def _build_tree(categories: list[Category]) -> list[CategoryTree]:
        """카테고리 목록을 트리 구조로 변환합니다.

        메모리에서 부모-자식 관계를 매핑하여 트리를 구성합니다.
        """
        # ID -> CategoryTree 매핑 생성
        tree_map: dict[int, CategoryTree] = {}
        for cat in categories:
            tree_map[cat.id] = CategoryTree(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                children=[],
            )

        # 부모-자식 관계 연결
        roots: list[CategoryTree] = []
        for cat in categories:
            tree_node = tree_map[cat.id]
            if cat.parent_id is not None and cat.parent_id in tree_map:
                tree_map[cat.parent_id].children.append(tree_node)
            else:
                roots.append(tree_node)

        return roots
