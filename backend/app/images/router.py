"""이미지 라우터 모듈

이미지 업로드, 조회, 삭제 엔드포인트를 정의합니다.
- POST /api/v1/images/upload - 이미지 업로드 (ADMIN 전용)
- GET /api/v1/images/{id} - 이미지 메타데이터 조회 (선택적 인증)
- DELETE /api/v1/images/{id} - 이미지 삭제 (ADMIN 전용)
"""

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_optional_user, require_admin
from app.auth.models import User
from app.common.responses import ApiResponse
from app.database import get_db
from app.images.schemas import ImageResponse, ImageUploadResponse
from app.images.service import ImageService

router = APIRouter(prefix="/api/v1/images", tags=["이미지"])


@router.post(
    "/upload",
    response_model=ApiResponse[ImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """이미지를 업로드합니다. (관리자 전용)

    지원 형식: JPEG, PNG, GIF, WebP
    업로드 시 리사이징 및 썸네일이 자동 생성됩니다.
    """
    service = ImageService(db)
    result = await service.upload_image(file)
    return ApiResponse(data=result)


@router.get("/{image_id}", response_model=ApiResponse[ImageResponse])
async def get_image(
    image_id: int,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """이미지 메타데이터를 조회합니다. (선택적 인증)"""
    service = ImageService(db)
    image = await service.get_image(image_id)
    return ApiResponse(data=ImageResponse.model_validate(image))


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """이미지를 삭제합니다. (관리자 전용)

    MinIO 스토리지와 DB에서 모두 삭제됩니다.
    """
    service = ImageService(db)
    await service.delete_image(image_id)
