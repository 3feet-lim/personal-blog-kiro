"""사용자 리포지토리 모듈

사용자 데이터 접근 로직을 담당합니다.
SQLAlchemy async session을 사용하여 CRUD 작업을 수행합니다.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.common.exceptions import DuplicateError, NotFoundError


class UserRepository:
    """사용자 데이터 접근 클래스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """ID로 사용자를 조회합니다."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """이메일로 사용자를 조회합니다."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        """모든 사용자 목록을 조회합니다."""
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        """새 사용자를 저장합니다.

        이메일 고유성을 검증한 후 사용자를 생성합니다.

        Raises:
            DuplicateError: 이메일이 이미 존재하는 경우
        """
        # 이메일 중복 검사
        existing = await self.get_by_email(user.email)
        if existing is not None:
            raise DuplicateError("이메일", user.email)

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def deactivate(self, user_id: int) -> User:
        """사용자를 비활성화합니다 (is_active = False).

        Raises:
            NotFoundError: 사용자가 존재하지 않는 경우
        """
        user = await self.get_by_id(user_id)
        if user is None:
            raise NotFoundError("사용자", str(user_id))

        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        return user
