"""FastAPI 앱 진입점

애플리케이션 생성 및 라우터 등록을 담당합니다.
"""

import logging

from contextlib import asynccontextmanager

from fastapi import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.common.exceptions import BlogException
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def _seed_admin() -> None:
    """DB에 admin 계정이 없으면 환경변수 기반으로 생성합니다."""
    from app.auth.models import User, UserRole
    from app.auth.service import AuthService
    from app.database import async_session
    from sqlalchemy import select

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == UserRole.ADMIN).limit(1)
        )
        if result.scalar_one_or_none() is None:
            admin = User(
                email=settings.admin_email,
                password_hash=AuthService.hash_password(settings.admin_password),
                name=settings.admin_name,
                role=UserRole.ADMIN,
            )
            session.add(admin)
            await session.commit()
            logger.info("초기 관리자 계정이 생성되었습니다: %s", settings.admin_email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _seed_admin()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="테크 블로그와 가족 사진을 하나의 플랫폼에서 관리하는 통합 블로그 API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 코드별 HTTP 상태 코드 매핑
_ERROR_STATUS_CODES: dict[str, int] = {
    "AUTH_FAILED": 401,
    "TOKEN_EXPIRED": 401,
    "PERMISSION_DENIED": 403,
    "NOT_FOUND": 404,
    "DUPLICATE": 409,
    "VALIDATION_ERROR": 400,
    "INVALID_IMAGE_FORMAT": 400,
    "CATEGORY_NOT_EMPTY": 409,
}


@app.exception_handler(BlogException)
async def blog_exception_handler(request: Request, exc: BlogException):
    """블로그 도메인 예외를 JSON 응답으로 변환하는 전역 핸들러"""
    return JSONResponse(
        status_code=_ERROR_STATUS_CODES.get(exc.error_code, 500),
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": getattr(exc, "details", None),
        },
    )


# 라우터 등록
from app.auth.router import router as auth_router
from app.auth.user_router import router as user_router
from app.categories.router import router as category_router
from app.images.router import router as image_router
from app.posts.router import router as post_router
from app.tags.router import post_tag_router, router as tag_router

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(post_router)
app.include_router(tag_router)
app.include_router(post_tag_router)
app.include_router(image_router)


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}
