/** 태그별 포스트 목록 페이지 */
"use client";

import { useState, useEffect, use } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { getPostsByTag } from "@/lib/api";
import PostCard from "@/components/posts/PostCard";
import Card from "@/components/ui/Card";
import type { PostListItem, PaginationMeta } from "@/types";

const PAGE_SIZE = 10;

export default function TagPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const searchParams = useSearchParams();
  const router = useRouter();
  const currentPage = Number(searchParams.get("page")) || 1;

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const result = await getPostsByTag(slug, {
          page: currentPage,
          size: PAGE_SIZE,
        });
        setPosts(result.data);
        setPagination(result.pagination);
      } catch { /* 무시 */ }
      setLoading(false);
    };
    fetchData();
  }, [slug, currentPage]);

  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    if (page === 1) params.delete("page");
    else params.set("page", String(page));
    const query = params.toString();
    router.push(query ? `/tag/${slug}?${query}` : `/tag/${slug}`);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-text-primary mb-6">
        태그: {slug}
      </h1>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-pulse h-24" />
          ))}
        </div>
      ) : posts.length > 0 ? (
        <>
          <div className="space-y-4">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
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
            이 태그에 해당하는 포스트가 없습니다.
          </p>
        </Card>
      )}
    </div>
  );
}
