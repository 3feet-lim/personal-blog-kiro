/** 가족 사진 목록 페이지 (비공개 - 인증 필요) */
"use client";

import { Suspense, useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { getPosts } from "@/lib/api";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { PostListItem, PaginationMeta } from "@/types";

/** 페이지당 포스트 수 */
const PAGE_SIZE = 12;

export default function FamilyPage() {
  return (
    <Suspense fallback={
      <div className="max-w-6xl mx-auto animate-pulse">
        <div className="h-7 bg-gray-200 rounded w-32 mb-6" />
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 h-48" />
          ))}
        </div>
      </div>
    }>
      <FamilyContent />
    </Suspense>
  );
}

function FamilyContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const currentPage = Number(searchParams.get("page")) || 1;

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);

  /** 인증되지 않은 사용자는 로그인 페이지로 리다이렉트 */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  /** 가족 포스트 목록 가져오기 (PRIVATE 포스트 포함) */
  const fetchPosts = useCallback(async (page: number) => {
    setLoading(true);
    try {
      const result = await getPosts({ page, size: PAGE_SIZE });
      // PRIVATE 포스트만 필터링 (가족 영역)
      setPosts(result.data.filter((p) => p.visibility === "private"));
      setPagination(result.pagination);
    } catch {
      setPosts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchPosts(currentPage);
    }
  }, [currentPage, isAuthenticated, fetchPosts]);

  /** 페이지 변경 */
  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    if (page === 1) params.delete("page");
    else params.set("page", String(page));
    const query = params.toString();
    router.push(query ? `/family?${query}` : "/family");
  };

  /** 인증 로딩 중 */
  if (authLoading) {
    return (
      <div className="max-w-6xl mx-auto animate-pulse">
        <div className="h-7 bg-gray-200 rounded w-32 mb-6" />
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 h-48" />
          ))}
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-text-primary">가족 앨범</h1>
        <Link
          href="/admin/posts/new"
          className="bg-blue-500 text-white rounded-md px-4 py-2 text-sm hover:bg-blue-600 transition-colors"
        >
          새 글 쓰기
        </Link>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="animate-pulse h-48" />
          ))}
        </div>
      ) : posts.length > 0 ? (
        <>
          {/* 이미지 그리드 레이아웃 */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {posts.map((post) => (
              <Link key={post.id} href={`/family/${post.slug}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
                  <h2 className="font-medium text-text-primary line-clamp-2">
                    {post.title}
                  </h2>
                  <div className="mt-2 text-xs text-text-secondary">
                    <time dateTime={post.created_at}>
                      {formatDate(post.created_at)}
                    </time>
                  </div>
                  {post.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {post.tags.map((tag) => (
                        <span
                          key={tag.id}
                          className="inline-block px-2 py-0.5 text-xs rounded-full bg-gray-100 text-text-secondary"
                        >
                          {tag.name}
                        </span>
                      ))}
                    </div>
                  )}
                </Card>
              </Link>
            ))}
          </div>

          {/* 페이지네이션 */}
          {pagination && pagination.total_pages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
                className="bg-white text-gray-700 border border-gray-300 rounded-md px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                이전
              </button>
              <span className="text-sm text-gray-600">
                {currentPage} / {pagination.total_pages}
              </span>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= pagination.total_pages}
                className="bg-white text-gray-700 border border-gray-300 rounded-md px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                다음
              </button>
            </div>
          )}
        </>
      ) : (
        <Card>
          <p className="text-text-secondary text-center py-8">
            아직 가족 앨범에 등록된 포스트가 없습니다.
          </p>
        </Card>
      )}
    </div>
  );
}
