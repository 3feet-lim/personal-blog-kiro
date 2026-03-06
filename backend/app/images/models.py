"""이미지 모델 모듈

Image SQLAlchemy 모델을 정의합니다.
업로드된 이미지의 원본, 리사이즈, 썸네일 URL과 메타데이터를 관리합니다.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Image(Base):
    """이미지 모델"""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_url = Column(String(500), nullable=False)
    resized_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=False)
    content_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 (PostImage와 다대다 연결)
    post_images = relationship("PostImage", back_populates="image")
