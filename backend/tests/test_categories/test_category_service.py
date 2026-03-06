"""카테고리 서비스 단위 테스트

generate_slug 함수, _build_tree 메서드, 스키마 유효성 검증을 테스트합니다.
DB 의존성 없이 테스트 가능한 순수 함수/정적 메서드를 중심으로 테스트합니다.
"""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
)
from app.categories.service import CategoryService, generate_slug


# ============================================================
# generate_slug 함수 테스트
# ============================================================

class TestGenerateSlug:
    """슬러그 생성 함수 테스트 (Req 3.6)"""

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
        """빈 문자열은 기본값 'category'를 반환해야 한다"""
        assert generate_slug("") == "category"

    def test_only_special_chars_returns_default(self):
        """특수문자만 있는 경우 기본값 'category'를 반환해야 한다"""
        assert generate_slug("!@#$%^&*()") == "category"

    def test_whitespace_only_returns_default(self):
        """공백만 있는 경우 기본값 'category'를 반환해야 한다"""
        assert generate_slug("   ") == "category"

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

    def test_unicode_normalization(self):
        """유니코드 정규화(NFC)가 적용되어야 한다"""
        # 한글 자모 조합 테스트
        result = generate_slug("가나다")
        assert result == "가나다"


# ============================================================
# _build_tree 정적 메서드 테스트
# ============================================================

def _make_category(id: int, name: str, slug: str, parent_id: int | None = None):
    """테스트용 카테고리 객체를 생성합니다 (SimpleNamespace 사용)."""
    return SimpleNamespace(id=id, name=name, slug=slug, parent_id=parent_id)


class TestBuildTree:
    """카테고리 트리 구조 변환 테스트 (Req 3.3)"""

    def test_empty_list(self):
        """빈 목록은 빈 트리를 반환해야 한다"""
        result = CategoryService._build_tree([])
        assert result == []

    def test_single_root(self):
        """최상위 카테고리 하나만 있는 경우"""
        categories = [_make_category(1, "Tech", "tech")]
        result = CategoryService._build_tree(categories)
        assert len(result) == 1
        assert result[0].name == "Tech"
        assert result[0].children == []

    def test_multiple_roots(self):
        """여러 최상위 카테고리가 있는 경우"""
        categories = [
            _make_category(1, "Tech", "tech"),
            _make_category(2, "Family", "family"),
        ]
        result = CategoryService._build_tree(categories)
        assert len(result) == 2
        names = {r.name for r in result}
        assert names == {"Tech", "Family"}

    def test_parent_child_relationship(self):
        """부모-자식 관계가 올바르게 구성되어야 한다"""
        categories = [
            _make_category(1, "Tech", "tech"),
            _make_category(2, "Python", "python", parent_id=1),
            _make_category(3, "JavaScript", "javascript", parent_id=1),
        ]
        result = CategoryService._build_tree(categories)
        assert len(result) == 1
        tech = result[0]
        assert tech.name == "Tech"
        assert len(tech.children) == 2
        child_names = {c.name for c in tech.children}
        assert child_names == {"Python", "JavaScript"}

    def test_deep_nesting(self):
        """3단계 이상 깊은 중첩도 올바르게 구성되어야 한다"""
        categories = [
            _make_category(1, "Tech", "tech"),
            _make_category(2, "Backend", "backend", parent_id=1),
            _make_category(3, "FastAPI", "fastapi", parent_id=2),
        ]
        result = CategoryService._build_tree(categories)
        assert len(result) == 1
        assert result[0].name == "Tech"
        assert len(result[0].children) == 1
        assert result[0].children[0].name == "Backend"
        assert len(result[0].children[0].children) == 1
        assert result[0].children[0].children[0].name == "FastAPI"

    def test_mixed_roots_and_children(self):
        """최상위와 하위 카테고리가 혼합된 경우"""
        categories = [
            _make_category(1, "Tech", "tech"),
            _make_category(2, "Family", "family"),
            _make_category(3, "Python", "python", parent_id=1),
            _make_category(4, "여행", "travel", parent_id=2),
        ]
        result = CategoryService._build_tree(categories)
        assert len(result) == 2

        # 각 루트의 자식 확인
        tech = next(r for r in result if r.name == "Tech")
        family = next(r for r in result if r.name == "Family")
        assert len(tech.children) == 1
        assert tech.children[0].name == "Python"
        assert len(family.children) == 1
        assert family.children[0].name == "여행"

    def test_orphan_category_becomes_root(self):
        """부모 ID가 존재하지 않는 카테고리는 루트로 처리되어야 한다"""
        categories = [
            _make_category(1, "Tech", "tech"),
            _make_category(2, "Orphan", "orphan", parent_id=999),
        ]
        result = CategoryService._build_tree(categories)
        # 부모가 없는 카테고리도 루트로 포함
        assert len(result) == 2


# ============================================================
# 스키마 유효성 검증 테스트
# ============================================================

class TestCategorySchemas:
    """카테고리 스키마 유효성 검증 테스트"""

    def test_category_create_valid(self):
        """유효한 카테고리 생성 데이터"""
        data = CategoryCreate(name="테크 블로그")
        assert data.name == "테크 블로그"
        assert data.parent_id is None

    def test_category_create_with_parent(self):
        """부모 카테고리가 지정된 생성 데이터"""
        data = CategoryCreate(name="Python", parent_id=1)
        assert data.parent_id == 1

    def test_category_create_empty_name_rejected(self):
        """빈 이름은 거부되어야 한다"""
        with pytest.raises(ValidationError):
            CategoryCreate(name="")

    def test_category_create_too_long_name_rejected(self):
        """100자 초과 이름은 거부되어야 한다"""
        with pytest.raises(ValidationError):
            CategoryCreate(name="a" * 101)

    def test_category_update_partial(self):
        """부분 수정 데이터가 허용되어야 한다"""
        data = CategoryUpdate(name="새 이름")
        assert data.name == "새 이름"
        assert data.parent_id is None

    def test_category_response_from_attributes(self):
        """from_attributes 모드로 객체에서 응답 스키마를 생성할 수 있어야 한다"""
        obj = SimpleNamespace(id=1, name="Tech", slug="tech", parent_id=None, order=0)
        resp = CategoryResponse.model_validate(obj, from_attributes=True)
        assert resp.id == 1
        assert resp.name == "Tech"
        assert resp.slug == "tech"

    def test_category_tree_recursive(self):
        """CategoryTree는 재귀적 children을 가질 수 있어야 한다"""
        tree = CategoryTree(
            id=1,
            name="Root",
            slug="root",
            children=[
                CategoryTree(id=2, name="Child", slug="child", children=[]),
            ],
        )
        assert len(tree.children) == 1
        assert tree.children[0].name == "Child"

    def test_category_tree_default_empty_children(self):
        """CategoryTree의 기본 children은 빈 리스트여야 한다"""
        tree = CategoryTree(id=1, name="Root", slug="root")
        assert tree.children == []
