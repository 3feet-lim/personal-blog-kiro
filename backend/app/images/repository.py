"""이미지 리포지토리 모듈

이미지 데이터 접근 로직을 담당합니다.
SQLAlchemy async session을 사용하여 CRUD 작업을 수행합니다.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.images.models import Image


class ImageRepository:
    """이미지 데이터 접근 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, image: Image) -> Image:
        """새 이미지 레코드를 저장합니다."""
        self.db.add(image)
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: int) -> Image | None:
        """ID로 이미지를 조회합니다."""
        result = await self.db.execute(
            select(Image).where(Image.id == image_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, image: Image) -> None:
        """이미지 레코드를 삭제합니다."""
        await self.db.delete(image)
        await self.db.flush()
