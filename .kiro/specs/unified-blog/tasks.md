# 구현 계획: 통합 블로그 시스템

## 개요

테크 블로그와 가족 사진을 통합 관리하는 블로그 시스템의 백엔드(FastAPI)와 프론트엔드(Next.js)를 구현합니다. 백엔드 API를 먼저 구현하고, 프론트엔드는 첫 페이지(레이아웃 + 홈 + 블로그 목록)를 우선 구현하여 디자인 리뷰를 거친 후 나머지 페이지를 구현합니다.

## 작업 목록

- [ ] 1. 프로젝트 초기 설정
  - [ ] 1.1 백엔드 프로젝트 구조 생성
    - `backend/` 디렉토리 및 하위 모듈 구조 생성
    - `requirements.txt` 작성 (FastAPI, SQLAlchemy, asyncpg, python-jose, passlib, Pillow, minio 등)
    - `app/config.py` 환경 설정 파일 작성
    - `app/database.py` 비동기 DB 연결 설정
    - _Requirements: 7.4_

  - [ ] 1.2 프론트엔드 프로젝트 구조 생성
    - Next.js 15.5.x 프로젝트 초기화
    - `src/` 디렉토리 구조 생성 (app, components, lib, hooks, types)
    - Tailwind CSS 설정 (라이트 모드 전용, 화이트 톤 기반 커스텀 색상)
    - _Requirements: 7.4_

  - [ ] 1.3 Docker Compose 설정 파일 작성
    - `docker-compose.yml` - PostgreSQL, MinIO, 백엔드, 프론트엔드 서비스 정의
    - 환경 변수 파일 (`.env.example`) 작성
    - 사용자가 직접 Docker 환경을 실행
    - _Requirements: 7.4_

- [ ] 2. 공통 모듈 구현
  - [ ] 2.1 공통 응답 스키마 및 예외 처리 구현
    - `app/common/responses.py` - ApiResponse, ErrorResponse, PaginatedResponse 스키마
    - `app/common/exceptions.py` - 커스텀 예외 클래스
    - `app/common/pagination.py` - 페이지네이션 유틸리티
    - 전역 예외 핸들러 등록
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

  - [ ]* 2.2 API 응답 형식 속성 테스트 작성
    - **Property 19: API 응답 형식 일관성**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [ ] 3. 인증 모듈 구현
  - [ ] 3.1 User 모델 및 스키마 구현
    - `app/auth/models.py` - User SQLAlchemy 모델 (OAuth 필드 포함)
    - `app/auth/schemas.py` - LoginRequest, TokenResponse, UserCreate, UserResponse 스키마
    - Alembic 마이그레이션 생성
    - _Requirements: 1.6, 1.7, 6.2_

  - [ ] 3.2 인증 서비스 구현
    - `app/auth/service.py` - AuthService 클래스
    - 비밀번호 해싱 (bcrypt)
    - JWT 토큰 생성/검증 (python-jose)
    - 로그인, 토큰 갱신 로직
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [ ] 3.3 인증 라우터 및 의존성 구현
    - `app/auth/router.py` - 로그인, 토큰 갱신, 현재 사용자 조회 엔드포인트
    - `app/auth/dependencies.py` - get_current_user, require_admin 의존성
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

  - [ ]* 3.4 인증 속성 테스트 작성
    - **Property 1: JWT 토큰 라운드트립**
    - **Property 2: 비밀번호 해싱 일관성**
    - **Property 3: 인증 실패 처리**
    - **Property 4: 토큰 갱신**
    - **Validates: Requirements 1.2, 1.3, 1.5, 1.6, 1.7**

- [ ] 4. 체크포인트 - 인증 모듈 검증
  - 사용자에게 테스트 실행 요청 (`pytest tests/test_auth/`)
  - 테스트 결과 확인 후 필요시 수정

- [ ] 5. 사용자 관리 구현
  - [ ] 5.1 사용자 리포지토리 및 서비스 구현
    - `app/auth/repository.py` - UserRepository 클래스
    - 사용자 생성, 목록 조회, 비활성화 로직
    - 이메일 고유성 검증
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

  - [ ] 5.2 사용자 관리 라우터 구현
    - 사용자 목록 조회, 생성, 비활성화 엔드포인트 (관리자 전용)
    - _Requirements: 6.1, 6.3, 6.4_

  - [ ]* 5.3 사용자 관리 속성 테스트 작성
    - **Property 17: 사용자 CRUD 일관성**
    - **Property 18: 이메일 고유성**
    - **Validates: Requirements 6.1, 6.3, 6.4, 6.5**

- [ ] 6. 카테고리 모듈 구현
  - [ ] 6.1 Category 모델 및 스키마 구현
    - `app/categories/models.py` - Category SQLAlchemy 모델 (자기 참조 관계)
    - `app/categories/schemas.py` - CategoryCreate, CategoryResponse, CategoryTree 스키마
    - Alembic 마이그레이션 생성
    - _Requirements: 3.6_

  - [ ] 6.2 카테고리 서비스 구현
    - `app/categories/service.py` - CategoryService 클래스
    - 카테고리 생성, 트리 조회, 삭제 로직
    - 슬러그 자동 생성
    - 포스트 존재 시 삭제 거부 로직
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 6.3 카테고리 라우터 구현
    - `app/categories/router.py` - CRUD 엔드포인트
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 6.4 카테고리 속성 테스트 작성
    - **Property 8: 카테고리 계층 구조 보존**
    - **Property 9: 카테고리 삭제 제약**
    - **Property 10: 카테고리 슬러그 고유성**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

- [ ] 7. 체크포인트 - 카테고리 모듈 검증
  - 사용자에게 테스트 실행 요청 (`pytest tests/test_categories/`)
  - 테스트 결과 확인 후 필요시 수정

- [ ] 8. 포스트 모듈 구현
  - [ ] 8.1 Post 모델 및 스키마 구현
    - `app/posts/models.py` - Post, PostImage SQLAlchemy 모델
    - `app/posts/schemas.py` - PostCreate, PostUpdate, PostResponse, PostListItem 스키마
    - Alembic 마이그레이션 생성
    - _Requirements: 2.4, 2.5_

  - [ ] 8.2 포스트 서비스 구현
    - `app/posts/service.py` - PostService 클래스
    - 포스트 CRUD 로직
    - 슬러그 자동 생성 및 고유성 보장
    - 접근 권한 기반 필터링 (PUBLIC/PRIVATE)
    - 페이지네이션
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 8.3 포스트 라우터 구현
    - `app/posts/router.py` - CRUD 및 목록 조회 엔드포인트
    - 선택적 인증 처리
    - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 8.4 포스트 속성 테스트 작성
    - **Property 5: 포스트 CRUD 라운드트립**
    - **Property 6: 포스트 타임스탬프 순서**
    - **Property 7: 슬러그 생성 및 고유성**
    - **Property 11: 접근 권한 기반 포스트 필터링**
    - **Property 12: 카테고리별 포스트 필터링**
    - **Property 13: 페이지네이션 일관성**
    - **Validates: Requirements 2.1-2.7, 4.1-4.6**

- [ ] 9. 태그 모듈 구현
  - [ ] 9.1 Tag, PostTag 모델 및 스키마 구현
    - `app/tags/__init__.py` - 태그 모듈 초기화
    - `app/tags/models.py` - Tag, PostTag SQLAlchemy 모델 (다대다 관계)
    - `app/tags/schemas.py` - TagCreate, TagUpdate, TagResponse 스키마
    - Alembic 마이그레이션 생성 (tags, post_tags 테이블)
    - _Requirements: 8.1, 8.4, 8.7, 8.8_

  - [ ] 9.2 태그 서비스 구현
    - `app/tags/service.py` - TagService 클래스
    - 태그 CRUD (생성, 수정, 삭제)
    - 태그 이름으로부터 슬러그 자동 생성
    - 태그 이름 고유성 검증 (중복 시 DuplicateError 반환)
    - 포스트-태그 다대다 관계 관리 (할당, 제거)
    - 태그별 포스트 필터링 조회
    - `app/tags/repository.py` - TagRepository 클래스
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9_

  - [ ] 9.3 태그 라우터 구현
    - `app/tags/router.py` - 태그 CRUD 엔드포인트
    - `POST /api/v1/tags` - 태그 생성 (ADMIN)
    - `PUT /api/v1/tags/{id}` - 태그 수정 (ADMIN)
    - `DELETE /api/v1/tags/{id}` - 태그 삭제 (ADMIN)
    - `GET /api/v1/tags` - 태그 목록 조회
    - `GET /api/v1/tags/{slug}/posts` - 태그별 포스트 필터링 (선택적 인증)
    - `POST /api/v1/posts/{id}/tags` - 포스트에 태그 할당 (ADMIN)
    - `DELETE /api/v1/posts/{id}/tags/{tag_id}` - 포스트에서 태그 제거 (ADMIN)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ]* 9.4 태그 속성 테스트 작성
    - **Property 20: 태그 CRUD 라운드트립**
    - 태그 생성 후 조회 시 동일한 이름과 슬러그가 반환되어야 하고, 수정 후 변경 내용이 반영되어야 하며, 삭제 후 포스트-태그 관계도 제거되어야 한다
    - **Validates: Requirements 8.1, 8.2, 8.3**

  - [ ]* 9.5 태그 슬러그 고유성 속성 테스트 작성
    - **Property 21: 태그 슬러그 고유성 및 이름 고유성**
    - 동일한 태그 이름으로 생성 시 중복 오류를 반환해야 하고, 생성된 슬러그는 URL-safe 문자만 포함해야 한다
    - **Validates: Requirements 8.7, 8.8, 8.9**

  - [ ]* 9.6 포스트-태그 다대다 관계 속성 테스트 작성
    - **Property 22: 포스트-태그 다대다 관계 일관성**
    - 포스트에 태그 할당 후 해당 태그로 필터링 시 포스트가 포함되어야 하고, 태그 제거 후 필터링 시 포스트가 제외되어야 한다
    - **Validates: Requirements 8.4, 8.5, 8.6**

- [ ] 10. 이미지 모듈 구현
  - [ ] 10.1 Image 모델 및 스키마 구현
    - `app/images/models.py` - Image SQLAlchemy 모델
    - `app/images/schemas.py` - ImageResponse, ImageUploadResponse 스키마
    - Alembic 마이그레이션 생성
    - _Requirements: 5.4_

  - [ ] 10.2 이미지 서비스 구현
    - `app/images/service.py` - ImageService 클래스
    - MinIO 클라이언트 설정
    - 이미지 업로드, 리사이징, 썸네일 생성 (Pillow)
    - 이미지 형식 검증
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [ ] 10.3 이미지 라우터 구현
    - `app/images/router.py` - 업로드, 조회, 삭제 엔드포인트
    - _Requirements: 5.1, 5.5_

  - [ ]* 10.4 이미지 속성 테스트 작성
    - **Property 14: 이미지 업로드 라운드트립**
    - **Property 15: 이미지 리사이징 제약**
    - **Property 16: 이미지 형식 검증**
    - **Validates: Requirements 5.1-5.7**

- [ ] 11. FastAPI 앱 통합
  - [ ] 11.1 메인 앱 설정
    - `app/main.py` - FastAPI 앱 생성, 라우터 등록 (태그 라우터 포함), CORS 설정
    - OpenAPI 문서 설정
    - _Requirements: 7.4_

  - [ ] 11.2 Alembic 설정 및 초기 마이그레이션
    - `alembic.ini` 설정
    - 전체 마이그레이션 스크립트 생성 (tags, post_tags 테이블 포함)
    - _Requirements: 2.5, 3.6, 8.8_

- [ ] 12. 체크포인트 - 백엔드 전체 검증
  - 사용자에게 전체 테스트 실행 요청 (`pytest tests/ -v`)
  - 테스트 결과 확인 후 필요시 수정

- [ ] 13. 프론트엔드 공통 모듈 구현
  - [ ] 13.1 API 클라이언트 및 타입 정의
    - `src/lib/api.ts` - Axios 기반 API 클라이언트
    - `src/types/index.ts` - TypeScript 타입 정의 (Tag, PostTag 타입 포함)
    - _Requirements: 7.4_

  - [ ] 13.2 인증 유틸리티 및 훅 구현
    - `src/lib/auth.ts` - 토큰 저장/조회 유틸리티
    - `src/hooks/useAuth.ts` - 인증 상태 관리 훅
    - _Requirements: 1.1, 1.3, 1.5_

- [ ] 14. 프론트엔드 첫 페이지 구현 (레이아웃 + 홈 + 블로그 목록)
  - [ ] 14.1 접이식 사이드바 레이아웃 구현
    - `src/components/layout/Sidebar.tsx` - 접이식 사이드바 (카테고리 트리, 네비게이션)
    - `src/components/layout/Header.tsx` - 헤더 (로고, 햄버거 메뉴, 로그인 버튼)
    - `src/components/layout/Footer.tsx` - 푸터
    - `src/app/layout.tsx` - 루트 레이아웃 (사이드바 + 메인 콘텐츠 구조)
    - 반응형: 모바일에서 사이드바 자동 접힘, 데스크톱에서 토글 가능
    - Tailwind CSS 화이트 톤 기반 스타일링
    - _Requirements: 4.4, 7.4_

  - [ ] 14.2 홈페이지 구현
    - `src/app/page.tsx` - 최신 포스트 미리보기, 카테고리 소개
    - 테크 블로그와 가족 영역 동일한 카드 스타일 적용
    - _Requirements: 4.1, 4.6_

  - [ ] 14.3 블로그 목록 페이지 구현
    - `src/app/(public)/blog/page.tsx` - 포스트 목록 (페이지네이션 포함)
    - `src/components/posts/PostCard.tsx` - 포스트 카드 컴포넌트
    - _Requirements: 4.1, 4.4, 4.6_

  - [ ] 14.4 에러 및 로딩 상태 UI 구현
    - `src/app/not-found.tsx` - 404 페이지 (홈으로 돌아가기 링크 포함)
    - `src/app/error.tsx` - 에러 바운더리 (`'use client'` 컴포넌트, 다시 시도하기 버튼, `reset()` 호출로 현재 경로 재로드)
    - `src/app/(public)/blog/loading.tsx` - 포스트 목록 스켈레톤 UI (카드 형태 플레이스홀더)
    - `src/app/(public)/blog/[slug]/loading.tsx` - 포스트 상세 스켈레톤 UI (제목, 메타데이터, 본문 플레이스홀더)
    - Tailwind CSS `animate-pulse` 활용한 스켈레톤 애니메이션
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [ ] 15. 디자인 리뷰 체크포인트
  - 사용자가 첫 페이지(레이아웃, 홈, 블로그 목록)의 디자인을 확인
  - 사이드바 동작, 색상, 레이아웃, 반응형 동작 등 피드백 수집
  - 에러/로딩 상태 UI 확인 (404 페이지, 에러 페이지, 스켈레톤 UI)
  - 피드백 반영 후 디자인 확정
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. 나머지 프론트엔드 페이지 구현
  - [ ] 16.1 로그인 페이지 구현
    - `src/app/login/page.tsx` - 로그인 폼 (화이트 톤 스타일)
    - _Requirements: 1.1, 1.2_

  - [ ] 16.2 비공개 가족 페이지 구현
    - `src/app/(private)/family/page.tsx` - 가족 사진 목록 (이미지 그리드 레이아웃)
    - `src/app/(private)/family/[slug]/page.tsx` - 가족 사진 상세
    - 인증 미들웨어 적용
    - 테크 블로그와 동일한 디자인 분위기 유지
    - _Requirements: 4.2, 4.3_

  - [ ] 16.3 관리자 페이지 구현
    - `src/app/admin/layout.tsx` - 관리자 레이아웃
    - `src/app/admin/posts/` - 포스트 관리 (목록, 생성, 수정)
    - `src/app/admin/categories/` - 카테고리 관리
    - `src/app/admin/tags/` - 태그 관리 (목록, 생성, 수정, 삭제)
    - `src/app/admin/users/` - 사용자 관리
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.4, 6.1, 6.3, 6.4, 8.1, 8.2, 8.3_

  - [ ] 16.4 마크다운 렌더러 구현
    - `src/components/posts/MarkdownRenderer.tsx` - 마크다운 렌더링
    - 코드 하이라이팅 지원
    - `src/app/(public)/blog/[slug]/page.tsx` - 포스트 상세 페이지 (태그 표시 포함)
    - `src/app/(public)/category/[slug]/page.tsx` - 카테고리별 포스트 페이지
    - `src/app/(public)/tag/[slug]/page.tsx` - 태그별 포스트 페이지
    - _Requirements: 2.4, 4.5, 8.6_

  - [ ] 16.5 이미지 업로드 컴포넌트 구현
    - `src/components/posts/ImageUploader.tsx` - 드래그앤드롭 이미지 업로드
    - 업로드 진행률 표시
    - 관리자 포스트 작성 페이지에 통합
    - _Requirements: 5.1_

- [ ] 17. 최종 체크포인트
  - 사용자에게 전체 통합 테스트 실행 요청
  - 백엔드: `pytest tests/ -v`
  - 프론트엔드: `npm run build && npm run lint`
  - 테스트 결과 확인 후 필요시 수정
  - Ensure all tests pass, ask the user if questions arise.

## 참고 사항

- `*` 표시된 작업은 선택적 테스트 작업으로 건너뛸 수 있습니다
- 각 작업은 해당 요구사항을 참조합니다
- 체크포인트에서 테스트 실패 시 이전 작업을 수정합니다
- 속성 테스트는 Hypothesis 라이브러리를 사용하여 최소 100회 반복 실행합니다
- **테스트 실행은 사용자에게 요청합니다** (Docker 환경 필요)
- 테스트 결과를 받은 후 필요한 수정 작업을 진행합니다
- **디자인 리뷰 체크포인트(15번)** 에서 사용자 피드백을 반영한 후 나머지 페이지를 구현합니다