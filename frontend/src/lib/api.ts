/** Axios 기반 API 클라이언트 - 백엔드 API 통신 유틸리티 */

import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  clearTokens,
} from "./auth";
import type {
  ApiResponse,
  PaginatedResponse,
  TokenResponse,
  LoginRequest,
  User,
  UserCreate,
  Post,
  PostListItem,
  PostCreate,
  PostUpdate,
  Category,
  CategoryTree,
  CategoryCreate,
  CategoryUpdate,
  Tag,
  TagCreate,
  TagUpdate,
  TagAssign,
  Image,
  ImageUploadResponse,
} from "@/types";

/** API 에러 클래스 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Axios 인스턴스 생성
 * Next.js rewrite 프록시를 사용하므로 상대 경로(/api/v1/...)로 요청
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

/** 토큰 갱신 중복 방지 플래그 */
let isRefreshing = false;
/** 토큰 갱신 대기 중인 요청 큐 */
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

/** 대기 큐의 모든 요청을 처리 */
function processQueue(error: unknown, token: string | null) {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });
  refreshQueue = [];
}

/** 요청 인터셉터 - Authorization 헤더에 Bearer 토큰 자동 주입 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/** 응답 인터셉터 - 401 에러 시 토큰 갱신 후 재요청 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // 401 에러이고 아직 재시도하지 않은 경우 토큰 갱신 시도
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      // 로그인/갱신 요청 자체가 실패한 경우는 재시도하지 않음
      const url = originalRequest.url || "";
      if (url.includes("/auth/login") || url.includes("/auth/refresh")) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // 이미 갱신 중이면 큐에 추가하고 대기
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(apiClient(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearTokens();
        isRefreshing = false;
        processQueue(error, null);
        return Promise.reject(error);
      }

      try {
        // 토큰 갱신 요청 (인터셉터를 거치지 않도록 axios 직접 사용)
        const { data } = await axios.post<ApiResponse<TokenResponse>>(
          "/api/v1/auth/refresh",
          { refresh_token: refreshToken },
          { headers: { "Content-Type": "application/json" } }
        );

        const newAccessToken = data.data.access_token;
        const newRefreshToken = data.data.refresh_token;

        setAccessToken(newAccessToken);
        setRefreshToken(newRefreshToken);

        // 대기 중인 요청들 처리
        processQueue(null, newAccessToken);

        // 원래 요청 재시도
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        // 갱신 실패 시 토큰 삭제
        clearTokens();
        processQueue(refreshError, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Axios 에러를 ApiError로 변환하는 헬퍼
 */
function handleApiError(error: unknown): never {
  if (error instanceof AxiosError && error.response) {
    const { status, data } = error.response;
    throw new ApiError(
      status,
      data?.error || "UNKNOWN_ERROR",
      data?.message || "알 수 없는 오류가 발생했습니다",
      data?.details
    );
  }
  if (error instanceof ApiError) {
    throw error;
  }
  throw new ApiError(0, "NETWORK_ERROR", "네트워크 연결을 확인해주세요");
}

// ─── 인증 API ───

/** 로그인 */
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  try {
    const { data } = await apiClient.post<ApiResponse<TokenResponse>>(
      "/auth/login",
      credentials
    );
    // 토큰 자동 저장
    setAccessToken(data.data.access_token);
    setRefreshToken(data.data.refresh_token);
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 토큰 갱신 */
export async function refreshToken(): Promise<TokenResponse> {
  try {
    const token = getRefreshToken();
    const { data } = await apiClient.post<ApiResponse<TokenResponse>>(
      "/auth/refresh",
      { refresh_token: token }
    );
    setAccessToken(data.data.access_token);
    setRefreshToken(data.data.refresh_token);
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 현재 사용자 정보 조회 */
export async function getMe(): Promise<User> {
  try {
    const { data } = await apiClient.get<ApiResponse<User>>("/auth/me");
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 로그아웃 */
export async function logout(): Promise<void> {
  try {
    await apiClient.post("/auth/logout");
  } catch {
    // 로그아웃 실패해도 로컬 토큰은 삭제
  } finally {
    clearTokens();
  }
}

// ─── 포스트 API ───

/** 포스트 목록 조회 (페이지네이션) */
export async function getPosts(params?: {
  page?: number;
  size?: number;
  category_id?: number;
}): Promise<PaginatedResponse<PostListItem>> {
  try {
    const { data } = await apiClient.get<PaginatedResponse<PostListItem>>(
      "/posts",
      { params }
    );
    return data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 포스트 상세 조회 (슬러그 기반) */
export async function getPostBySlug(slug: string): Promise<Post> {
  try {
    const { data } = await apiClient.get<ApiResponse<Post>>(
      `/posts/${slug}`
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 포스트 생성 */
export async function createPost(postData: PostCreate): Promise<Post> {
  try {
    const { data } = await apiClient.post<ApiResponse<Post>>(
      "/posts",
      postData
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 포스트 수정 */
export async function updatePost(
  id: number,
  postData: PostUpdate
): Promise<Post> {
  try {
    const { data } = await apiClient.put<ApiResponse<Post>>(
      `/posts/${id}`,
      postData
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 포스트 삭제 */
export async function deletePost(id: number): Promise<void> {
  try {
    await apiClient.delete(`/posts/${id}`);
  } catch (error) {
    handleApiError(error);
  }
}

// ─── 카테고리 API ───

/** 카테고리 트리 조회 */
export async function getCategories(): Promise<CategoryTree[]> {
  try {
    const { data } = await apiClient.get<ApiResponse<CategoryTree[]>>(
      "/categories"
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 카테고리 생성 */
export async function createCategory(
  categoryData: CategoryCreate
): Promise<Category> {
  try {
    const { data } = await apiClient.post<ApiResponse<Category>>(
      "/categories",
      categoryData
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 카테고리 수정 */
export async function updateCategory(
  id: number,
  categoryData: CategoryUpdate
): Promise<Category> {
  try {
    const { data } = await apiClient.put<ApiResponse<Category>>(
      `/categories/${id}`,
      categoryData
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 카테고리 삭제 */
export async function deleteCategory(id: number): Promise<void> {
  try {
    await apiClient.delete(`/categories/${id}`);
  } catch (error) {
    handleApiError(error);
  }
}

// ─── 태그 API ───

/** 태그 목록 조회 */
export async function getTags(): Promise<Tag[]> {
  try {
    const { data } = await apiClient.get<ApiResponse<Tag[]>>("/tags");
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 태그 생성 */
export async function createTag(tagData: TagCreate): Promise<Tag> {
  try {
    const { data } = await apiClient.post<ApiResponse<Tag>>("/tags", tagData);
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 태그 수정 */
export async function updateTag(
  id: number,
  tagData: TagUpdate
): Promise<Tag> {
  try {
    const { data } = await apiClient.put<ApiResponse<Tag>>(
      `/tags/${id}`,
      tagData
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 태그 삭제 */
export async function deleteTag(id: number): Promise<void> {
  try {
    await apiClient.delete(`/tags/${id}`);
  } catch (error) {
    handleApiError(error);
  }
}

/** 태그별 포스트 목록 조회 */
export async function getPostsByTag(
  slug: string,
  params?: { page?: number; size?: number }
): Promise<PaginatedResponse<PostListItem>> {
  try {
    const { data } = await apiClient.get<PaginatedResponse<PostListItem>>(
      `/tags/${slug}/posts`,
      { params }
    );
    return data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 포스트에 태그 할당 */
export async function assignTagToPost(
  postId: number,
  tagData: TagAssign
): Promise<void> {
  try {
    await apiClient.post(`/posts/${postId}/tags`, tagData);
  } catch (error) {
    handleApiError(error);
  }
}

/** 포스트에서 태그 제거 */
export async function removeTagFromPost(
  postId: number,
  tagId: number
): Promise<void> {
  try {
    await apiClient.delete(`/posts/${postId}/tags/${tagId}`);
  } catch (error) {
    handleApiError(error);
  }
}

// ─── 이미지 API ───

/** 이미지 업로드 (multipart/form-data) */
export async function uploadImage(file: File): Promise<ImageUploadResponse> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await apiClient.post<ApiResponse<ImageUploadResponse>>(
      "/images/upload",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 이미지 상세 조회 */
export async function getImage(id: number): Promise<Image> {
  try {
    const { data } = await apiClient.get<ApiResponse<Image>>(
      `/images/${id}`
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 이미지 삭제 */
export async function deleteImage(id: number): Promise<void> {
  try {
    await apiClient.delete(`/images/${id}`);
  } catch (error) {
    handleApiError(error);
  }
}

// ─── 사용자 관리 API (관리자 전용) ───

/** 사용자 목록 조회 */
export async function getUsers(): Promise<User[]> {
  try {
    const { data } = await apiClient.get<ApiResponse<User[]>>("/users");
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 사용자 생성 */
export async function createUser(userData: UserCreate): Promise<User> {
  try {
    const { data } = await apiClient.post<ApiResponse<User>>(
      "/users",
      userData
    );
    return data.data;
  } catch (error) {
    handleApiError(error);
  }
}

/** 사용자 비활성화 */
export async function deactivateUser(id: number): Promise<void> {
  try {
    await apiClient.delete(`/users/${id}`);
  } catch (error) {
    handleApiError(error);
  }
}

/** Axios 인스턴스 내보내기 (커스텀 요청이 필요한 경우) */
export { apiClient };
