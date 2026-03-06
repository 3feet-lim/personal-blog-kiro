/** TypeScript 타입 정의 - 백엔드 스키마와 매칭 */

/** 사용자 역할 */
export type UserRole = "admin" | "family_member";

/** 포스트 공개 범위 */
export type Visibility = "public" | "private";

// ─── 사용자 관련 타입 ───

/** 사용자 */
export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

/** 사용자 생성 요청 */
export interface UserCreate {
  email: string;
  password: string;
  name: string;
  role?: UserRole;
}

// ─── 카테고리 관련 타입 ───

/** 카테고리 */
export interface Category {
  id: number;
  name: string;
  slug: string;
  parent_id: number | null;
  order: number;
}

/** 카테고리 트리 (계층 구조) */
export interface CategoryTree {
  id: number;
  name: string;
  slug: string;
  children: CategoryTree[];
}

/** 카테고리 생성 요청 */
export interface CategoryCreate {
  name: string;
  parent_id?: number | null;
}

/** 카테고리 수정 요청 */
export interface CategoryUpdate {
  name?: string;
  parent_id?: number | null;
}


// ─── 태그 관련 타입 ───

/** 태그 */
export interface Tag {
  id: number;
  name: string;
  slug: string;
  created_at: string;
}

/** 태그 생성 요청 */
export interface TagCreate {
  name: string;
}

/** 태그 수정 요청 */
export interface TagUpdate {
  name?: string;
}

/** 포스트에 태그 할당 요청 */
export interface TagAssign {
  tag_id: number;
}

// ─── 포스트 관련 타입 ───

/** 포스트 상세 */
export interface Post {
  id: number;
  title: string;
  slug: string;
  content: string;
  visibility: Visibility;
  author: User;
  category: Category | null;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

/** 포스트 목록 아이템 */
export interface PostListItem {
  id: number;
  title: string;
  slug: string;
  visibility: Visibility;
  author_name: string;
  category_name: string | null;
  tags: Tag[];
  created_at: string;
}

/** 포스트 생성 요청 */
export interface PostCreate {
  title: string;
  content: string;
  visibility?: Visibility;
  category_id?: number | null;
  tag_ids?: number[];
}

/** 포스트 수정 요청 */
export interface PostUpdate {
  title?: string;
  content?: string;
  visibility?: Visibility;
  category_id?: number | null;
  tag_ids?: number[];
}

// ─── 이미지 관련 타입 ───

/** 이미지 상세 */
export interface Image {
  id: number;
  filename: string;
  original_url: string;
  resized_url: string;
  thumbnail_url: string;
  content_type: string;
  file_size: number;
  created_at: string;
}

/** 포스트-이미지 관계 */
export interface PostImage {
  id: number;
  post_id: number;
  image_id: number;
  order: number;
}

/** 이미지 업로드 응답 */
export interface ImageUploadResponse {
  id: number;
  url: string;
  thumbnail_url: string;
}

// ─── 인증 관련 타입 ───

/** 로그인 요청 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** 토큰 응답 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ─── 공통 응답 타입 ───

/** 페이지네이션 메타데이터 */
export interface PaginationMeta {
  page: number;
  size: number;
  total: number;
  total_pages: number;
}

/** API 성공 응답 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/** API 에러 응답 */
export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

/** 페이지네이션 응답 */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}
