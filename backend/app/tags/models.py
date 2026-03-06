"""태그 모델 모듈

Tag, PostTag SQLAlchemy 모델을 정의합니다.
포스트와 태그 간의 다대다 관계를 지원합니다.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Tag(Base):
    """태그 모델

    포스트에 할당할 수 있는 횡단적 분류 키워드입니다.
    이름과 슬러그는 고유해야 합니다.
    """
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 관계: PostTag를 통한 다대다
    post_tags = relationship("PostTag", back_populates="tag", cascade="all, delete-orphan")


class PostTag(Base):
    """포스트-태그 연결 모델 (다대다 중간 테이블)

    포스트와 태그 간의 다대다 관계를 관리합니다.
    동일한 포스트-태그 조합의 중복을 방지합니다.
    """
    __tablename__ = "post_tags"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)

    # 동일한 포스트-태그 조합 중복 방지
    __table_args__ = (
        UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
    )

    # 관계
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")
