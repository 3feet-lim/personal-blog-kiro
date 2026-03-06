"""카테고리 모델 모듈

Category SQLAlchemy 모델을 정의합니다.
자기 참조 관계를 통해 계층적 카테고리 구조를 지원합니다.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Category(Base):
    """카테고리 모델

    계층적 트리 구조를 지원하는 카테고리입니다.
    parent_id를 통해 자기 참조 관계를 형성합니다.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 자기 참조 관계 (부모-자식)
    parent = relationship(
        "Category", remote_side=[id], back_populates="children"
    )
    children = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan"
    )

    # 포스트 관계 (Post 모델이 아직 없으므로 문자열 참조)
    posts = relationship("Post", back_populates="category")
