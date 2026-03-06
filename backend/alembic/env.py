"""Alembic 환경 설정 모듈

비동기 마이그레이션을 지원하며, 모든 모델의 metadata를 자동으로 등록합니다.
DATABASE_URL 환경 변수에서 DB 연결 정보를 읽어옵니다.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config 객체 (alembic.ini 값에 접근)
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모든 모델을 import하여 Base.metadata에 등록
from app.database import Base  # noqa: E402
from app.auth.models import User, UserRole  # noqa: E402, F401
from app.categories.models import Category  # noqa: E402, F401
from app.posts.models import Post, PostImage, Visibility  # noqa: E402, F401
from app.images.models import Image  # noqa: E402, F401
from app.tags.models import Tag, PostTag  # noqa: E402, F401

# 마이그레이션 대상 metadata
target_metadata = Base.metadata

# 환경 변수에서 DATABASE_URL을 읽어 sqlalchemy.url 설정
from app.config import get_settings  # noqa: E402

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """오프라인 모드에서 마이그레이션 실행

    DB 연결 없이 SQL 스크립트만 생성합니다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """실제 마이그레이션 실행 (동기 컨텍스트)"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진으로 마이그레이션 실행"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드에서 마이그레이션 실행

    비동기 엔진을 사용하여 DB에 직접 마이그레이션을 적용합니다.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
