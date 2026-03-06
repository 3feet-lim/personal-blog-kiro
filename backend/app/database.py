"""비동기 데이터베이스 연결 설정 모듈

SQLAlchemy Async 엔진과 세션을 설정합니다.
asyncpg 드라이버를 사용하여 PostgreSQL에 비동기로 연결합니다.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# 비동기 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 비동기 세션 팩토리
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 모델 기본 클래스"""
    pass


async def get_db() -> AsyncSession:
    """비동기 DB 세션을 제공하는 의존성 함수

    FastAPI의 Depends()와 함께 사용합니다.
    요청 처리 후 세션을 자동으로 닫습니다.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
