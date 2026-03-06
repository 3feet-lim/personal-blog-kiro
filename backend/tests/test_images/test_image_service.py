"""이미지 서비스 단위 테스트

validate_image_format, resize_image, create_thumbnail 함수를 테스트합니다.
DB/MinIO 의존성 없이 테스트 가능한 순수 함수를 중심으로 테스트합니다.
"""

import io

import pytest
from PIL import Image as PILImage

from app.common.exceptions import ImageFormatError
from app.images.service import (
    SUPPORTED_FORMATS,
    create_thumbnail,
    resize_image,
    validate_image_format,
)


def _create_test_image(
    width: int = 800,
    height: int = 600,
    fmt: str = "PNG",
    color: str = "red",
) -> bytes:
    """테스트용 이미지 바이트 데이터를 생성합니다."""
    img = PILImage.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


# ============================================================
# validate_image_format 테스트
# ============================================================

class TestValidateImageFormat:
    """이미지 형식 검증 테스트 (Req 5.6, 5.7)"""

    def test_jpeg_accepted(self):
        """JPEG 형식은 허용되어야 한다"""
        result = validate_image_format("image/jpeg")
        assert result == "image/jpeg"

    def test_png_accepted(self):
        """PNG 형식은 허용되어야 한다"""
        result = validate_image_format("image/png")
        assert result == "image/png"

    def test_gif_accepted(self):
        """GIF 형식은 허용되어야 한다"""
        result = validate_image_format("image/gif")
        assert result == "image/gif"

    def test_webp_accepted(self):
        """WebP 형식은 허용되어야 한다"""
        result = validate_image_format("image/webp")
        assert result == "image/webp"

    def test_unsupported_format_rejected(self):
        """지원하지 않는 형식은 ImageFormatError를 발생시켜야 한다"""
        with pytest.raises(ImageFormatError):
            validate_image_format("image/bmp")

    def test_none_content_type_rejected(self):
        """None content_type은 ImageFormatError를 발생시켜야 한다"""
        with pytest.raises(ImageFormatError):
            validate_image_format(None)

    def test_text_format_rejected(self):
        """텍스트 형식은 거부되어야 한다"""
        with pytest.raises(ImageFormatError):
            validate_image_format("text/plain")

    def test_all_supported_formats(self):
        """SUPPORTED_FORMATS에 정의된 모든 형식이 허용되어야 한다"""
        for content_type in SUPPORTED_FORMATS:
            result = validate_image_format(content_type)
            assert result == content_type


# ============================================================
# resize_image 테스트
# ============================================================

class TestResizeImage:
    """이미지 리사이징 테스트 (Req 5.2)"""

    def test_large_image_resized(self):
        """최대 크기보다 큰 이미지는 축소되어야 한다"""
        original = _create_test_image(2000, 1500)
        max_size = (1920, 1080)

        resized_data = resize_image(original, max_size)
        img = PILImage.open(io.BytesIO(resized_data))

        assert img.width <= max_size[0]
        assert img.height <= max_size[1]

    def test_small_image_unchanged(self):
        """최대 크기 이내의 이미지는 원본 그대로 반환되어야 한다"""
        original = _create_test_image(800, 600)
        max_size = (1920, 1080)

        resized_data = resize_image(original, max_size)
        # 원본 데이터와 동일해야 함
        assert resized_data == original

    def test_aspect_ratio_preserved(self):
        """리사이징 시 원본 비율이 유지되어야 한다"""
        # 4:3 비율 이미지
        original = _create_test_image(4000, 3000)
        max_size = (1920, 1080)

        resized_data = resize_image(original, max_size)
        img = PILImage.open(io.BytesIO(resized_data))

        # 비율 확인 (약간의 반올림 오차 허용)
        original_ratio = 4000 / 3000
        resized_ratio = img.width / img.height
        assert abs(original_ratio - resized_ratio) < 0.01

    def test_exact_max_size_unchanged(self):
        """정확히 최대 크기인 이미지는 원본 그대로 반환되어야 한다"""
        original = _create_test_image(1920, 1080)
        max_size = (1920, 1080)

        resized_data = resize_image(original, max_size)
        assert resized_data == original

    def test_wide_image_resized_correctly(self):
        """가로가 긴 이미지도 올바르게 리사이징되어야 한다"""
        original = _create_test_image(3840, 500)
        max_size = (1920, 1080)

        resized_data = resize_image(original, max_size)
        img = PILImage.open(io.BytesIO(resized_data))

        assert img.width <= max_size[0]
        assert img.height <= max_size[1]


# ============================================================
# create_thumbnail 테스트
# ============================================================

class TestCreateThumbnail:
    """썸네일 생성 테스트 (Req 5.3)"""

    def test_thumbnail_created(self):
        """썸네일이 생성되어야 한다"""
        original = _create_test_image(1920, 1080)
        thumbnail_data = create_thumbnail(original)

        img = PILImage.open(io.BytesIO(thumbnail_data))
        assert img.width <= 300
        assert img.height <= 300

    def test_thumbnail_custom_size(self):
        """커스텀 크기로 썸네일을 생성할 수 있어야 한다"""
        original = _create_test_image(1920, 1080)
        custom_size = (200, 200)

        thumbnail_data = create_thumbnail(original, size=custom_size)
        img = PILImage.open(io.BytesIO(thumbnail_data))

        assert img.width <= custom_size[0]
        assert img.height <= custom_size[1]

    def test_thumbnail_preserves_aspect_ratio(self):
        """썸네일 생성 시 원본 비율이 유지되어야 한다"""
        # 16:9 비율 이미지
        original = _create_test_image(1600, 900)
        thumbnail_data = create_thumbnail(original, size=(300, 300))

        img = PILImage.open(io.BytesIO(thumbnail_data))

        original_ratio = 1600 / 900
        thumb_ratio = img.width / img.height
        assert abs(original_ratio - thumb_ratio) < 0.01

    def test_small_image_thumbnail(self):
        """작은 이미지도 썸네일이 생성되어야 한다"""
        original = _create_test_image(100, 100)
        thumbnail_data = create_thumbnail(original, size=(300, 300))

        img = PILImage.open(io.BytesIO(thumbnail_data))
        # 원본이 썸네일 크기보다 작으면 원본 크기 유지
        assert img.width <= 300
        assert img.height <= 300

    def test_thumbnail_is_valid_image(self):
        """생성된 썸네일은 유효한 이미지여야 한다"""
        original = _create_test_image(1920, 1080, fmt="PNG")
        thumbnail_data = create_thumbnail(original)

        # 유효한 이미지로 열 수 있어야 함
        img = PILImage.open(io.BytesIO(thumbnail_data))
        img.verify()  # 이미지 무결성 검증
