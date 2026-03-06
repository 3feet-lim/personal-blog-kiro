"""공통 응답 스키마 단위 테스트"""

from app.common.responses import (
    ApiResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
)


class TestApiResponse:
    """ApiResponse 스키마 테스트"""

    def test_data_with_message(self):
        """data와 message가 포함된 응답 생성"""
        resp = ApiResponse[str](data="hello", message="성공")
        assert resp.data == "hello"
        assert resp.message == "성공"

    def test_data_without_message(self):
        """message 없이 data만 포함된 응답 생성"""
        resp = ApiResponse[int](data=42)
        assert resp.data == 42
        assert resp.message is None

    def test_dict_data(self):
        """dict 타입 data 응답"""
        resp = ApiResponse[dict](data={"id": 1, "name": "test"})
        assert resp.data["id"] == 1

    def test_serialization_includes_data_field(self):
        """직렬화 시 data 필드 포함 확인 (요구사항 7.1)"""
        resp = ApiResponse[str](data="test")
        dumped = resp.model_dump()
        assert "data" in dumped


class TestErrorResponse:
    """ErrorResponse 스키마 테스트"""

    def test_error_with_details(self):
        """error, message, details가 포함된 오류 응답"""
        resp = ErrorResponse(
            error="VALIDATION_ERROR",
            message="유효하지 않은 입력",
            details={"field": "email"},
        )
        assert resp.error == "VALIDATION_ERROR"
        assert resp.message == "유효하지 않은 입력"
        assert resp.details == {"field": "email"}

    def test_error_without_details(self):
        """details 없는 오류 응답"""
        resp = ErrorResponse(error="NOT_FOUND", message="찾을 수 없습니다")
        assert resp.details is None

    def test_serialization_includes_error_and_message(self):
        """직렬화 시 error, message 필드 포함 확인 (요구사항 7.2)"""
        resp = ErrorResponse(error="ERR", message="msg")
        dumped = resp.model_dump()
        assert "error" in dumped
        assert "message" in dumped
