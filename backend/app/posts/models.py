"""포스트 모델 모듈

Post, PostImage SQLAlchemy 모델을 정의합니다.
포스트의 공개 범위(Visibility)와 이미지 연결 관계를 지원합니다.
"""

from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Visibility(str, PyEnum):
    """포스트 공개 범위"""
    PUBLIC = "public"
    PRIVATE = "private"


class Post(Base):
    """포스트 모델"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    visibility = Column(
        SQLEnum(Visibility, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Visibility.PUBLIC,
    )
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    published_at = Column(DateTime(timezone=True), nullable=True)

    # 관계
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    post_tags = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")


class PostImage(Base):
    """포스트-이미지 연결 모델 (다대다 중간 테이블)"""
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    order = Column(Integer, default=0)

    # 관계
    post = relationship("Post", back_populates="images")
    image = relationship("Image", back_populates="post_images")
