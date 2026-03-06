"""이미지 서비스 모듈

이미지 업로드, 리사이징, 썸네일 생성, 형식 검증 등
비즈니스 로직을 담당합니다.
MinIO 스토리지와 Pillow를 사용합니다.
"""

import io
import uuid

from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ImageFormatError, NotFoundError
from app.config import get_settings
from app.images.models import Image
from app.images.repository import ImageRepository
from app.images.schemas import ImageUploadResponse

# 지원하는 이미지 형식 (MIME 타입 -> 확장자 매핑)
SUPPORTED_FORMATS: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}

# Pillow 형식 이름 -> MIME 타입 매핑
PILLOW_FORMAT_MAP: dict[str, str] = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "GIF": "image/gif",
    "WEBP": "image/webp",
}


def _get_minio_client() -> Minio:
    """MinIO 클라이언트를 생성합니다."""
    settings = get_settings()
    return Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_use_ssl,
    )


def _ensure_bucket_exists(client: Minio, bucket_name: str) -> None:
    """MinIO 버킷이 존재하지 않으면 생성합니다."""
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def validate_image_format(content_type: str | None) -> str:
    """이미지 형식을 검증합니다.

    Args:
        content_type: 업로드된 파일의 MIME 타입

    Returns:
        검증된 content_type 문자열

    Raises:
        ImageFormatError: 지원하지 않는 형식인 경우
    """
    if content_type is None or content_type not in SUPPORTED_FORMATS:
        raise ImageFormatError(content_type or "unknown")
    return content_type


def resize_image(
    image_data: bytes,
    max_size: tuple[int, int],
) -> bytes:
    """이미지를 지정된 최대 크기로 리사이징합니다.

    원본 비율을 유지하면서 max_size 이내로 축소합니다.
    이미 max_size 이내인 경우 원본을 그대로 반환합니다.

    Args:
        image_data: 원본 이미지 바이트 데이터
        max_size: (최대 너비, 최대 높이) 튜플

    Returns:
        리사이징된 이미지 바이트 데이터
    """
    img = PILImage.open(io.BytesIO(image_data))
    original_format = img.format or "PNG"

    # 이미 최대 크기 이내이면 원본 반환
    if img.width <= max_size[0] and img.height <= max_size[1]:
        return image_data

    # 비율 유지하며 리사이징
    img.thumbnail(max_size, PILImage.LANCZOS)

    output = io.BytesIO()
    # GIF 애니메이션 보존을 위해 save_all 사용
    save_kwargs: dict = {"format": original_format}
    if original_format == "GIF":
        save_kwargs["save_all"] = True
    if original_format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = 85

    img.save(output, **save_kwargs)
    return output.getvalue()


def create_thumbnail(
    image_data: bytes,
    size: tuple[int, int] = (300, 300),
) -> bytes:
    """썸네일 이미지를 생성합니다.

    지정된 크기로 비율을 유지하며 축소합니다.

    Args:
        image_data: 원본 이미지 바이트 데이터
        size: (너비, 높이) 튜플, 기본값 (300, 300)

    Returns:
        썸네일 이미지 바이트 데이터
    """
    img = PILImage.open(io.BytesIO(image_data))
    original_format = img.format or "PNG"

    img.thumbnail(size, PILImage.LANCZOS)

    output = io.BytesIO()
    save_kwargs: dict = {"format": original_format}
    if original_format == "GIF":
        save_kwargs["save_all"] = True
    if original_format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = 85

    img.save(output, **save_kwargs)
    return output.getvalue()


class ImageService:
    """이미지 비즈니스 로직을 처리하는 서비스 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ImageRepository(db)
        self.settings = get_settings()
        self.minio_client = _get_minio_client()
        self.bucket_name = self.settings.minio_bucket_name

        # 버킷 존재 확인 및 생성
        _ensure_bucket_exists(self.minio_client, self.bucket_name)

    async def upload_image(self, file: UploadFile) -> ImageUploadResponse:
        """이미지를 업로드하고 리사이징, 썸네일을 생성합니다.

        1. 이미지 형식 검증
        2. 원본 이미지를 MinIO에 저장
        3. 리사이즈 이미지를 MinIO에 저장
        4. 썸네일 이미지를 MinIO에 저장
        5. DB에 이미지 메타데이터 저장

        Args:
            file: 업로드된 파일 (FastAPI UploadFile)

        Returns:
            ImageUploadResponse: 업로드 결과 (id, url, thumbnail_url)

        Raises:
            ImageFormatError: 지원하지 않는 이미지 형식인 경우
        """
        # 1. 형식 검증
        content_type = validate_image_format(file.content_type)
        ext = SUPPORTED_FORMATS[content_type]

        # 2. 파일 데이터 읽기
        file_data = await file.read()
        file_size = len(file_data)

        # 3. 고유 파일명 생성
        unique_id = uuid.uuid4().hex
        original_key = f"original/{unique_id}{ext}"
        resized_key = f"resized/{unique_id}{ext}"
        thumbnail_key = f"thumbnail/{unique_id}{ext}"

        # 4. 리사이징 및 썸네일 생성
        max_size = (self.settings.image_max_width, self.settings.image_max_height)
        thumb_size = (self.settings.thumbnail_width, self.settings.thumbnail_height)

        resized_data = resize_image(file_data, max_size)
        thumbnail_data = create_thumbnail(file_data, thumb_size)

        # 5. MinIO에 업로드 (원본, 리사이즈, 썸네일)
        self._upload_to_minio(original_key, file_data, content_type)
        self._upload_to_minio(resized_key, resized_data, content_type)
        self._upload_to_minio(thumbnail_key, thumbnail_data, content_type)

        # 6. URL 생성
        original_url = self._build_url(original_key)
        resized_url = self._build_url(resized_key)
        thumbnail_url = self._build_url(thumbnail_key)

        # 7. DB에 메타데이터 저장
        image = Image(
            filename=file.filename or f"{unique_id}{ext}",
            original_url=original_url,
            resized_url=resized_url,
            thumbnail_url=thumbnail_url,
            content_type=content_type,
            file_size=file_size,
        )
        image = await self.repo.create(image)

        return ImageUploadResponse(
            id=image.id,
            url=resized_url,
            thumbnail_url=thumbnail_url,
        )

    async def get_image_url(self, image_id: int, size: str = "resized") -> str:
        """이미지 URL을 조회합니다.

        Args:
            image_id: 이미지 ID
            size: 이미지 크기 ("original", "resized", "thumbnail")

        Returns:
            이미지 URL 문자열

        Raises:
            NotFoundError: 이미지가 존재하지 않는 경우
        """
        image = await self.repo.get_by_id(image_id)
        if image is None:
            raise NotFoundError("이미지", str(image_id))

        url_map = {
            "original": image.original_url,
            "resized": image.resized_url,
            "thumbnail": image.thumbnail_url,
        }
        return url_map.get(size, image.resized_url)

    async def get_image(self, image_id: int) -> Image:
        """이미지 메타데이터를 조회합니다.

        Args:
            image_id: 이미지 ID

        Returns:
            Image 모델 객체

        Raises:
            NotFoundError: 이미지가 존재하지 않는 경우
        """
        image = await self.repo.get_by_id(image_id)
        if image is None:
            raise NotFoundError("이미지", str(image_id))
        return image

    async def delete_image(self, image_id: int) -> None:
        """이미지를 삭제합니다.

        MinIO에서 원본, 리사이즈, 썸네일 파일을 삭제하고
        DB에서 메타데이터를 삭제합니다.

        Args:
            image_id: 삭제할 이미지 ID

        Raises:
            NotFoundError: 이미지가 존재하지 않는 경우
        """
        image = await self.repo.get_by_id(image_id)
        if image is None:
            raise NotFoundError("이미지", str(image_id))

        # MinIO에서 파일 삭제 (실패해도 DB 삭제는 진행)
        for url in [image.original_url, image.resized_url, image.thumbnail_url]:
            self._delete_from_minio(url)

        await self.repo.delete(image)

    def _upload_to_minio(
        self, object_name: str, data: bytes, content_type: str
    ) -> None:
        """MinIO에 파일을 업로드합니다."""
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def _build_url(self, object_name: str) -> str:
        """MinIO 오브젝트의 URL을 생성합니다."""
        protocol = "https" if self.settings.minio_use_ssl else "http"
        return f"{protocol}://{self.settings.minio_endpoint}/{self.bucket_name}/{object_name}"

    def _delete_from_minio(self, url: str) -> None:
        """URL에서 오브젝트 키를 추출하여 MinIO에서 삭제합니다."""
        try:
            # URL에서 버킷명 이후의 경로를 오브젝트 키로 추출
            prefix = f"/{self.bucket_name}/"
            idx = url.find(prefix)
            if idx == -1:
                return
            object_name = url[idx + len(prefix):]
            self.minio_client.remove_object(self.bucket_name, object_name)
        except S3Error:
            # MinIO 삭제 실패는 무시 (로그만 남기고 진행)
            pass
