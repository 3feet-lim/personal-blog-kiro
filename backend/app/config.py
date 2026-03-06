"""환경 설정 모듈

pydantic-settings 기반으로 환경 변수를 관리합니다.
.env 파일 또는 시스템 환경 변수에서 설정값을 로드합니다.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 환경 설정"""

    # 앱 기본 설정
    app_name: str = "통합 블로그 시스템"
    app_version: str = "1.0.0"
    debug: bool = False

    # 데이터베이스 설정
    database_url: str = "postgresql+asyncpg://blog:blog@localhost:5432/blog"

    # JWT 인증 설정
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # MinIO 스토리지 설정
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "blog-images"
    minio_use_ssl: bool = False

    # 이미지 처리 설정
    image_max_width: int = 1920
    image_max_height: int = 1080
    thumbnail_width: int = 300
    thumbnail_height: int = 300

    # CORS 설정
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스를 반환합니다."""
    return Settings()
