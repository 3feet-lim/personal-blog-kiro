"""포스트 서비스 모듈

포스트 생성, 수정, 삭제, 조회 등 비즈니스 로직을 담당합니다.
슬러그 자동 생성, 접근 권한 기반 필터링, 페이지네이션을 포함합니다.
"""

import re
import unicodedata

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.common.exceptions import NotFoundError, PermissionDeniedError
from app.common.pagination import paginate
from app.common.responses import PaginatedResponse
from app.posts.models import Post, Visibility
from app.posts.repository import PostRepository
from app.posts.schemas import PostCreate, PostUpdate
from app.tags.models import PostTag, Tag


def generate_slug(title: str) -> str:
    """포스트 제목에서 URL-safe 슬러그를 생성합니다.

    한글, 영문, 숫자를 지원합니다.
    - 영문/숫자: 소문자로 변환하여 유지
    - 한글: 그대로 유지
    - 공백 및 특수문자: 하이픈(-)으로 변환
    - 연속 하이픈 제거, 앞뒤 하이픈 제거
    """
    # 유니코드 정규화 (NFC)
    text = unicodedata.normalize("NFC", title.strip())

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
        text = "post"

    return text


class PostService:
    """포스트 비즈니스 로직을 처리하는 서비스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PostRepository(db)

    async def create_post(self, post_data: PostCreate, author_id: int) -> Post:
        """새 포스트를 생성합니다.

        제목에서 슬러그를 자동 생성하고 고유성을 보장합니다.

        Args:
            post_data: 포스트 생성 데이터
            author_id: 작성자 ID

        Returns:
            생성된 Post 객체
        """
        # 슬러그 자동 생성 (고유성 보장)
        base_slug = generate_slug(post_data.title)
        slug = await self._ensure_unique_slug(base_slug)

        post = Post(
            title=post_data.title,
            slug=slug,
            content=post_data.content,
            visibility=post_data.visibility,
            author_id=author_id,
            category_id=post_data.category_id,
        )
        post = await self.repo.create(post)
        await self._sync_tags(post, post_data.tag_ids)
        return post

    async def update_post(self, post_id: int, post_data: PostUpdate) -> Post:
        """포스트를 수정합니다.

        제목 변경 시 슬러그를 재생성합니다.

        Args:
            post_id: 수정할 포스트 ID
            post_data: 수정할 데이터

        Returns:
            수정된 Post 객체

        Raises:
            NotFoundError: 포스트가 존재하지 않는 경우
        """
        post = await self.repo.get_by_id(post_id)
        if post is None:
            raise NotFoundError("포스트", str(post_id))

        # 제목 변경 시 슬러그 재생성
        if post_data.title is not None:
            post.title = post_data.title
            base_slug = generate_slug(post_data.title)
            if base_slug != post.slug:
                post.slug = await self._ensure_unique_slug(base_slug)

        if post_data.content is not None:
            post.content = post_data.content

        if post_data.visibility is not None:
            post.visibility = post_data.visibility

        if post_data.category_id is not None:
            post.category_id = post_data.category_id

        if post_data.tag_ids is not None:
            await self._sync_tags(post, post_data.tag_ids)

        return await self.repo.update(post)

    async def delete_post(self, post_id: int) -> None:
        """포스트를 삭제합니다.

        Args:
            post_id: 삭제할 포스트 ID

        Raises:
            NotFoundError: 포스트가 존재하지 않는 경우
        """
        post = await self.repo.get_by_id(post_id)
        if post is None:
            raise NotFoundError("포스트", str(post_id))

        await self.repo.delete(post)

    async def get_post_by_slug(self, slug: str, user: User | None) -> Post:
        """슬러그로 포스트를 조회합니다.

        인증되지 않은 사용자가 PRIVATE 포스트에 접근하면
        PermissionDeniedError를 발생시킵니다.

        Args:
            slug: 포스트 슬러그
            user: 현재 인증된 사용자 (None이면 비인증)

        Returns:
            조회된 Post 객체

        Raises:
            NotFoundError: 포스트가 존재하지 않는 경우
            PermissionDeniedError: 비인증 사용자가 PRIVATE 포스트 접근 시
        """
        post = await self.repo.get_by_slug(slug)
        if post is None:
            raise NotFoundError("포스트", slug)

        # 비인증 사용자가 PRIVATE 포스트에 접근하면 거부
        if post.visibility == Visibility.PRIVATE and user is None:
            raise PermissionDeniedError("비공개 포스트에 접근할 수 없습니다")

        return post

    async def get_posts(
        self,
        user: User | None,
        category_id: int | None,
        page: int,
        size: int,
    ) -> PaginatedResponse:
        """포스트 목록을 조회합니다.

        인증되지 않은 사용자에게는 PUBLIC 포스트만 반환하고,
        인증된 사용자에게는 모든 포스트를 반환합니다.

        Args:
            user: 현재 인증된 사용자 (None이면 비인증)
            category_id: 카테고리 필터 (None이면 전체)
            page: 페이지 번호 (1부터 시작)
            size: 페이지당 항목 수

        Returns:
            PaginatedResponse: 페이지네이션된 포스트 목록
        """
        # 비인증 사용자는 PUBLIC만 조회
        visibility = Visibility.PUBLIC if user is None else None

        offset = (page - 1) * size
        posts = await self.repo.get_list(visibility, category_id, offset, size)
        total = await self.repo.count(visibility, category_id)

        return paginate(posts, total, page, size)

    async def _sync_tags(self, post: Post, tag_ids: list[int]) -> None:
        """포스트의 태그를 동기화합니다.

        기존 태그를 모두 제거하고 새 태그 목록으로 교체합니다.
        """
        # 기존 태그 관계 제거
        post.post_tags.clear()
        await self.db.flush()

        # 새 태그 연결
        for tag_id in tag_ids:
            post.post_tags.append(PostTag(post_id=post.id, tag_id=tag_id))
        await self.db.flush()

    async def _ensure_unique_slug(self, base_slug: str) -> str:
        """슬러그의 고유성을 보장합니다.

        동일한 슬러그가 존재하면 숫자 접미사를 추가합니다.
        예: "my-post" -> "my-post-1" -> "my-post-2"
        """
        slug = base_slug
        counter = 1

        while await self.repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug
