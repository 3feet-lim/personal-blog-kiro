"""포스트 서비스 단위 테스트

generate_slug 함수, 스키마 유효성 검증을 테스트합니다.
DB 의존성 없이 테스트 가능한 순수 함수를 중심으로 테스트합니다.
"""

import pytest
from pydantic import ValidationError

from app.posts.models import Visibility
from app.posts.schemas import PostCreate, PostUpdate, PostListItem
from app.posts.service import generate_slug


# ============================================================
# generate_slug 함수 테스트
# ============================================================

class TestGenerateSlug:
    """포스트 슬러그 생성 함수 테스트 (Req 2.6, 2.7)"""

    def test_english_lowercase(self):
        """영문은 소문자로 변환되어야 한다"""
        assert generate_slug("Hello World") == "hello-world"

    def test_korean_preserved(self):
        """한글은 그대로 유지되어야 한다"""
        result = generate_slug("기술 블로그")
        assert "기술" in result
        assert "블로그" in result
        assert result == "기술-블로그"

    def test_mixed_korean_english(self):
        """한글과 영문이 혼합된 경우 모두 유지되어야 한다"""
        result = generate_slug("Python 개발 가이드")
        assert result == "python-개발-가이드"

    def test_numbers_preserved(self):
        """숫자는 유지되어야 한다"""
        assert generate_slug("Chapter 3") == "chapter-3"

    def test_special_characters_removed(self):
        """특수문자는 제거되어야 한다"""
        result = generate_slug("Hello! @World# $Test")
        assert result == "hello-world-test"

    def test_consecutive_spaces(self):
        """연속 공백은 하나의 하이픈으로 변환되어야 한다"""
        result = generate_slug("hello   world")
        assert result == "hello-world"

    def test_leading_trailing_spaces(self):
        """앞뒤 공백은 제거되어야 한다"""
        result = generate_slug("  hello world  ")
        assert result == "hello-world"

    def test_empty_string_returns_default(self):
        """빈 문자열은 기본값 'post'를 반환해야 한다"""
        assert generate_slug("") == "post"

    def test_only_special_chars_returns_default(self):
        """특수문자만 있는 경우 기본값 'post'를 반환해야 한다"""
        assert generate_slug("!@#$%^&*()") == "post"

    def test_whitespace_only_returns_default(self):
        """공백만 있는 경우 기본값 'post'를 반환해야 한다"""
        assert generate_slug("   ") == "post"

    def test_hyphens_preserved(self):
        """하이픈은 유지되어야 한다"""
        result = generate_slug("front-end")
        assert result == "front-end"

    def test_underscores_converted_to_hyphens(self):
        """언더스코어는 하이픈으로 변환되어야 한다"""
        result = generate_slug("hello_world")
        assert result == "hello-world"

    def test_consecutive_hyphens_collapsed(self):
        """연속 하이픈은 하나로 합쳐져야 한다"""
        result = generate_slug("hello---world")
        assert result == "hello-world"

    def test_url_safe_characters_only(self):
        """생성된 슬러그는 URL-safe 문자만 포함해야 한다"""
        import re
        # URL-safe: 영문 소문자, 숫자, 하이픈, 한글
        url_safe_pattern = re.compile(r"^[a-z0-9가-힣-]+$")
        test_titles = [
            "Hello World",
            "Python 개발 가이드",
            "Chapter 3: Advanced Topics!",
            "가족 여행 2024",
        ]
        for title in test_titles:
            slug = generate_slug(title)
            assert url_safe_pattern.match(slug), f"슬러그 '{slug}'에 URL-unsafe 문자가 포함됨"


# ============================================================
# 스키마 유효성 검증 테스트
# ============================================================

class TestPostSchemas:
    """포스트 스키마 유효성 검증 테스트"""

    def test_post_create_valid(self):
        """유효한 포스트 생성 데이터"""
        data = PostCreate(title="테스트 포스트", content="# 내용입니다")
        assert data.title == "테스트 포스트"
        assert data.content == "# 내용입니다"
        assert data.visibility == Visibility.PUBLIC
        assert data.category_id is None

    def test_post_create_with_all_fields(self):
        """모든 필드가 지정된 포스트 생성 데이터"""
        data = PostCreate(
            title="비공개 포스트",
            content="비공개 내용",
            visibility=Visibility.PRIVATE,
            category_id=1,
        )
        assert data.visibility == Visibility.PRIVATE
        assert data.category_id == 1

    def test_post_create_empty_title_rejected(self):
        """빈 제목은 거부되어야 한다"""
        with pytest.raises(ValidationError):
            PostCreate(title="", content="내용")

    def test_post_create_empty_content_rejected(self):
        """빈 내용은 거부되어야 한다"""
        with pytest.raises(ValidationError):
            PostCreate(title="제목", content="")

    def test_post_create_too_long_title_rejected(self):
        """255자 초과 제목은 거부되어야 한다"""
        with pytest.raises(ValidationError):
            PostCreate(title="a" * 256, content="내용")

    def test_post_update_partial(self):
        """부분 수정 데이터가 허용되어야 한다"""
        data = PostUpdate(title="새 제목")
        assert data.title == "새 제목"
        assert data.content is None
        assert data.visibility is None

    def test_post_update_all_none(self):
        """모든 필드가 None인 수정 데이터도 허용되어야 한다"""
        data = PostUpdate()
        assert data.title is None
        assert data.content is None
        assert data.visibility is None
        assert data.category_id is None

    def test_post_create_default_visibility(self):
        """기본 공개 범위는 PUBLIC이어야 한다"""
        data = PostCreate(title="제목", content="내용")
        assert data.visibility == Visibility.PUBLIC

    def test_post_list_item_from_attributes(self):
        """from_attributes 모드로 PostListItem을 생성할 수 있어야 한다"""
        from types import SimpleNamespace
        from datetime import datetime, timezone

        obj = SimpleNamespace(
            id=1,
            title="테스트",
            slug="test",
            visibility=Visibility.PUBLIC,
            author_name="관리자",
            category_name="기술",
            created_at=datetime.now(timezone.utc),
        )
        item = PostListItem.model_validate(obj, from_attributes=True)
        assert item.id == 1
        assert item.title == "테스트"
        assert item.slug == "test"
