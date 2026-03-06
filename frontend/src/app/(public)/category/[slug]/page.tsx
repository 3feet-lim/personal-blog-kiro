/** 카테고리별 포스트 목록 페이지 */
"use client";

import { useState, useEffect, useCallback, use } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { getPosts, getCategories } from "@/lib/api";
import PostCard from "@/components/posts/PostCard";
import Card from "@/components/ui/Card";
import type { PostListItem, PaginationMeta, CategoryTree } from "@/types";

const PAGE_SIZE = 10;

export default function CategoryPage({
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
  const [categoryName, setCategoryName] = useState<string>("");
  const [loading, setLoading] = useState(true);

  /** 카테고리 트리에서 slug로 카테고리 찾기 */
  const findCategory = useCallback(
    (cats: CategoryTree[], targetSlug: string): CategoryTree | null => {
      for (const cat of cats) {
        if (cat.slug === targetSlug) return cat;
        if (cat.children?.length) {
          const found = findCategory(cat.children, targetSlug);
          if (found) return found;
        }
      }
      return null;
    },
    []
  );

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // 카테고리 정보 가져오기
        const categories = await getCategories();
        const category = findCategory(categories, slug);
        if (category) {
          setCategoryName(category.name);
          // 해당 카테고리의 포스트 가져오기
          const result = await getPosts({
            page: currentPage,
            size: PAGE_SIZE,
            category_id: category.id,
          });
          setPosts(result.data);
          setPagination(result.pagination);
        }
      } catch { /* 무시 */ }
      setLoading(false);
    };
    fetchData();
  }, [slug, currentPage, findCategory]);

  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    if (page === 1) params.delete("page");
    else params.set("page", String(page));
    const query = params.toString();
    router.push(query ? `/category/${slug}?${query}` : `/category/${slug}`);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-text-primary mb-6">
        {categoryName || slug}
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
            이 카테고리에 포스트가 없습니다.
          </p>
        </Card>
      )}
    </div>
  );
}
