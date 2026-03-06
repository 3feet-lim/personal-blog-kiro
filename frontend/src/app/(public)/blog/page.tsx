/** 블로그 목록 페이지 - 포스트 목록 및 페이지네이션 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import PostCard from "@/components/posts/PostCard";
import { getPosts } from "@/lib/api";
import type { PostListItem, PaginationMeta } from "@/types";

/** 페이지당 포스트 수 */
const PAGE_SIZE = 10;

/** 포스트 목록 스켈레톤 UI */
function PostListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 animate-pulse"
        >
          {/* 제목 스켈레톤 */}
          <div className="h-5 bg-gray-200 rounded w-3/4" />
          {/* 메타 정보 스켈레톤 */}
          <div className="mt-3 flex items-center gap-3">
            <div className="h-4 bg-gray-200 rounded w-16" />
            <div className="h-4 bg-gray-200 rounded w-20" />
            <div className="h-4 bg-gray-200 rounded w-24" />
          </div>
          {/* 태그 스켈레톤 */}
          <div className="mt-3 flex gap-1">
            <div className="h-5 bg-gray-100 rounded-full w-12" />
            <div className="h-5 bg-gray-100 rounded-full w-16" />
          </div>
        </div>
      ))}
    </div>
  );
}

/** 빈 상태 UI */
function EmptyState() {
  return (
    <div className="text-center py-16">
      <p className="text-gray-500 text-lg">아직 작성된 포스트가 없습니다.</p>
    </div>
  );
}

/** 페이지네이션 컨트롤 */
function Pagination({
  pagination,
  onPageChange,
}: {
  pagination: PaginationMeta;
  onPageChange: (page: number) => void;
}) {
  const { page, total_pages } = pagination;

  if (total_pages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-4 mt-8">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="bg-white text-gray-700 border border-gray-300 rounded-md px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        이전
      </button>
      <span className="text-sm text-gray-600">
        {page} / {total_pages}
      </span>
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= total_pages}
        className="bg-white text-gray-700 border border-gray-300 rounded-md px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        다음
      </button>
    </div>
  );
}

/** 블로그 목록 페이지 */
export default function BlogListPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  /** URL 쿼리에서 현재 페이지 번호 추출 */
  const currentPage = Number(searchParams.get("page")) || 1;

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /** 포스트 목록 가져오기 */
  const fetchPosts = useCallback(async (page: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getPosts({ page, size: PAGE_SIZE });
      setPosts(result.data);
      setPagination(result.pagination);
    } catch {
      setError("포스트를 불러오는 데 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  /** 페이지 변경 시 데이터 다시 가져오기 */
  useEffect(() => {
    fetchPosts(currentPage);
  }, [currentPage, fetchPosts]);

  /** 페이지 변경 핸들러 - URL 쿼리 파라미터 업데이트 */
  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    if (page === 1) {
      params.delete("page");
    } else {
      params.set("page", String(page));
    }
    const query = params.toString();
    router.push(query ? `/blog?${query}` : "/blog");
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">블로그</h1>

      {/* 로딩 상태 */}
      {loading && <PostListSkeleton />}

      {/* 에러 상태 */}
      {!loading && error && (
        <div className="text-center py-16">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={() => fetchPosts(currentPage)}
            className="bg-blue-500 text-white rounded-md px-4 py-2 hover:bg-blue-600"
          >
            다시 시도
          </button>
        </div>
      )}

      {/* 빈 상태 */}
      {!loading && !error && posts.length === 0 && <EmptyState />}

      {/* 포스트 목록 */}
      {!loading && !error && posts.length > 0 && (
        <>
          <div className="space-y-4">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>

          {/* 페이지네이션 */}
          {pagination && (
            <Pagination
              pagination={pagination}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
    </div>
  );
}
