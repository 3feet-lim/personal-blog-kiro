"""이미지 스키마 모듈

이미지 관련 Pydantic 스키마를 정의합니다.
이미지 상세 응답과 업로드 응답 스키마를 포함합니다.
"""

from datetime import datetime

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """이미지 상세 응답 스키마"""
    id: int
    filename: str
    original_url: str
    resized_url: str
    thumbnail_url: str
    content_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ImageUploadResponse(BaseModel):
    """이미지 업로드 응답 스키마"""
    id: int
    url: str
    thumbnail_url: str
