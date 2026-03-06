"""페이지네이션 유틸리티 단위 테스트"""

from app.common.pagination import paginate


class TestPaginate:
    """paginate 헬퍼 함수 테스트"""

    def test_basic_pagination(self):
        """기본 페이지네이션 메타데이터 계산"""
        result = paginate(items=["a", "b", "c"], total=10, page=1, size=3)
        assert result.data == ["a", "b", "c"]
        assert result.pagination.page == 1
        assert result.pagination.size == 3
        assert result.pagination.total == 10
        assert result.pagination.total_pages == 4  # ceil(10/3) = 4

    def test_exact_division(self):
        """전체 항목이 페이지 크기로 나누어 떨어지는 경우"""
        result = paginate(items=[1, 2], total=6, page=3, size=2)
        assert result.pagination.total_pages == 3

    def test_single_page(self):
        """전체 항목이 한 페이지에 들어가는 경우"""
        result = paginate(items=[1, 2, 3], total=3, page=1, size=10)
        assert result.pagination.total_pages == 1

    def test_empty_items(self):
        """빈 결과"""
        result = paginate(items=[], total=0, page=1, size=10)
        assert result.data == []
        assert result.pagination.total == 0
        assert result.pagination.total_pages == 0

    def test_zero_size(self):
        """페이지 크기가 0인 경우 total_pages는 0"""
        result = paginate(items=[], total=5, page=1, size=0)
        assert result.pagination.total_pages == 0

    def test_pagination_meta_in_response(self):
        """응답에 pagination 메타데이터 포함 확인 (요구사항 7.3)"""
        result = paginate(items=[1], total=1, page=1, size=10)
        dumped = result.model_dump()
        assert "pagination" in dumped
        assert "page" in dumped["pagination"]
        assert "size" in dumped["pagination"]
        assert "total" in dumped["pagination"]
        assert "total_pages" in dumped["pagination"]
