"""태그 서비스 모듈

태그 생성, 수정, 삭제, 조회 등 비즈니스 로직을 담당합니다.
슬러그 자동 생성, 이름 고유성 검증, 포스트-태그 관계 관리를 포함합니다.
"""

import re
import unicodedata

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.common.exceptions import DuplicateError, NotFoundError
from app.common.pagination import paginate
from app.common.responses import PaginatedResponse
from app.posts.models import Visibility
from app.tags.models import Tag
from app.tags.repository import TagRepository
from app.tags.schemas import TagCreate, TagUpdate


def generate_slug(name: str) -> str:
    """태그 이름에서 URL-safe 슬러그를 생성합니다.

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
        text = "tag"

    return text


class TagService:
    """태그 비즈니스 로직을 처리하는 서비스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TagRepository(db)

    async def create_tag(self, tag_data: TagCreate) -> Tag:
        """새 태그를 생성합니다.

        이름에서 슬러그를 자동 생성하고, 이름 고유성을 검증합니다.

        Args:
            tag_data: 태그 생성 데이터

        Returns:
            생성된 Tag 객체

        Raises:
            DuplicateError: 동일한 태그 이름이 이미 존재하는 경우
        """
        # 태그 이름 고유성 검증
        if await self.repo.name_exists(tag_data.name):
            raise DuplicateError("태그 이름", tag_data.name)

        # 슬러그 자동 생성 (고유성 보장)
        base_slug = generate_slug(tag_data.name)
        slug = await self._ensure_unique_slug(base_slug)

        tag = Tag(name=tag_data.name, slug=slug)
        return await self.repo.create(tag)

    async def update_tag(self, tag_id: int, tag_data: TagUpdate) -> Tag:
        """태그를 수정합니다.

        이름 변경 시 슬러그를 재생성하고, 이름 고유성을 검증합니다.

        Args:
            tag_id: 수정할 태그 ID
            tag_data: 수정할 데이터

        Returns:
            수정된 Tag 객체

        Raises:
            NotFoundError: 태그가 존재하지 않는 경우
            DuplicateError: 동일한 태그 이름이 이미 존재하는 경우
        """
        tag = await self.repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("태그", str(tag_id))

        if tag_data.name is not None:
            # 이름 고유성 검증 (자기 자신 제외)
            if await self.repo.name_exists(tag_data.name, exclude_id=tag_id):
                raise DuplicateError("태그 이름", tag_data.name)

            tag.name = tag_data.name

            # 슬러그 재생성
            base_slug = generate_slug(tag_data.name)
            if base_slug != tag.slug:
                tag.slug = await self._ensure_unique_slug(base_slug)

        return await self.repo.update(tag)

    async def delete_tag(self, tag_id: int) -> None:
        """태그를 삭제합니다.

        cascade 설정으로 포스트-태그 관계도 함께 삭제됩니다.

        Args:
            tag_id: 삭제할 태그 ID

        Raises:
            NotFoundError: 태그가 존재하지 않는 경우
        """
        tag = await self.repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("태그", str(tag_id))

        await self.repo.delete(tag)

    async def get_tag_by_id(self, tag_id: int) -> Tag:
        """ID로 태그를 조회합니다.

        Raises:
            NotFoundError: 태그가 존재하지 않는 경우
        """
        tag = await self.repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("태그", str(tag_id))
        return tag

    async def get_tag_by_slug(self, slug: str) -> Tag:
        """슬러그로 태그를 조회합니다.

        Raises:
            NotFoundError: 태그가 존재하지 않는 경우
        """
        tag = await self.repo.get_by_slug(slug)
        if tag is None:
            raise NotFoundError("태그", slug)
        return tag

    async def get_all_tags(self) -> list[Tag]:
        """모든 태그를 조회합니다."""
        return await self.repo.get_all()

    # ── 포스트-태그 관계 관리 ──

    async def assign_tag_to_post(self, post_id: int, tag_id: int) -> None:
        """포스트에 태그를 할당합니다.

        포스트와 태그의 존재 여부를 검증한 후 관계를 생성합니다.

        Args:
            post_id: 포스트 ID
            tag_id: 태그 ID

        Raises:
            NotFoundError: 포스트 또는 태그가 존재하지 않는 경우
        """
        # 태그 존재 여부 검증
        tag = await self.repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("태그", str(tag_id))

        # 포스트 존재 여부 검증
        from app.posts.repository import PostRepository
        post_repo = PostRepository(self.db)
        post = await post_repo.get_by_id(post_id)
        if post is None:
            raise NotFoundError("포스트", str(post_id))

        await self.repo.assign_tag_to_post(post_id, tag_id)

    async def remove_tag_from_post(self, post_id: int, tag_id: int) -> None:
        """포스트에서 태그를 제거합니다.

        Args:
            post_id: 포스트 ID
            tag_id: 태그 ID

        Raises:
            NotFoundError: 포스트 또는 태그가 존재하지 않는 경우
        """
        # 태그 존재 여부 검증
        tag = await self.repo.get_by_id(tag_id)
        if tag is None:
            raise NotFoundError("태그", str(tag_id))

        # 포스트 존재 여부 검증
        from app.posts.repository import PostRepository
        post_repo = PostRepository(self.db)
        post = await post_repo.get_by_id(post_id)
        if post is None:
            raise NotFoundError("포스트", str(post_id))

        await self.repo.remove_tag_from_post(post_id, tag_id)

    async def get_posts_by_tag(
        self,
        tag_slug: str,
        user: User | None,
        page: int,
        size: int,
    ) -> PaginatedResponse:
        """태그별 포스트 목록을 조회합니다.

        인증되지 않은 사용자에게는 PUBLIC 포스트만 반환하고,
        인증된 사용자에게는 모든 포스트를 반환합니다.

        Args:
            tag_slug: 태그 슬러그
            user: 현재 인증된 사용자 (None이면 비인증)
            page: 페이지 번호 (1부터 시작)
            size: 페이지당 항목 수

        Returns:
            PaginatedResponse: 페이지네이션된 포스트 목록

        Raises:
            NotFoundError: 태그가 존재하지 않는 경우
        """
        tag = await self.repo.get_by_slug(tag_slug)
        if tag is None:
            raise NotFoundError("태그", tag_slug)

        # 비인증 사용자는 PUBLIC만 조회
        visibility = Visibility.PUBLIC if user is None else None

        offset = (page - 1) * size
        posts = await self.repo.get_posts_by_tag(tag.id, visibility, offset, size)
        total = await self.repo.count_posts_by_tag(tag.id, visibility)

        return paginate(posts, total, page, size)

    async def _ensure_unique_slug(self, base_slug: str) -> str:
        """슬러그의 고유성을 보장합니다.

        동일한 슬러그가 존재하면 숫자 접미사를 추가합니다.
        예: "python" -> "python-1" -> "python-2"
        """
        slug = base_slug
        counter = 1

        while await self.repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug
