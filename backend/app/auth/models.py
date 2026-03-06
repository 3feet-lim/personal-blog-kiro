"""사용자 모델 모듈

User SQLAlchemy 모델을 정의합니다.
역할 기반 접근 제어(RBAC)와 OAuth 확장을 지원합니다.
"""

from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, PyEnum):
    """사용자 역할"""
    ADMIN = "admin"
    FAMILY_MEMBER = "family_member"


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # OAuth 사용자는 null 가능
    name = Column(String(100), nullable=False)
    role = Column(
        SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.FAMILY_MEMBER,
    )
    is_active = Column(Boolean, default=True)

    # OAuth 확장 필드 (추후 SSO 구현 시 사용)
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 관계
    posts = relationship("Post", back_populates="author")
