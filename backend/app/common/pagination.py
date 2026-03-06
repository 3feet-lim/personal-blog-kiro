"""페이지네이션 유틸리티 모듈

목록 조회 시 페이지네이션 메타데이터를 계산하는 헬퍼 함수를 제공합니다.
"""

import math

from app.common.responses import PaginatedResponse, PaginationMeta


def paginate(items: list, total: int, page: int, size: int) -> PaginatedResponse:
    """페이지네이션된 응답을 생성합니다.

    Args:
        items: 현재 페이지의 항목 리스트
        total: 전체 항목 수
        page: 현재 페이지 번호 (1부터 시작)
        size: 페이지당 항목 수

    Returns:
        PaginatedResponse: 페이지네이션 메타데이터가 포함된 응답
    """
    total_pages = math.ceil(total / size) if size > 0 else 0

    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
        ),
    )
