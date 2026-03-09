/** 관리자 - 포스트 관리 페이지 (목록, 삭제, 글쓰기/수정 페이지 연결) */
"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getPosts, deletePost } from "@/lib/api";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { PostListItem, PaginationMeta } from "@/types";

export default function AdminPostsPage() {
  const router = useRouter();
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const fetchPosts = useCallback(async (p: number) => {
    setLoading(true);
    try {
      const result = await getPosts({ page: p, size: 20 });
      setPosts(result.data);
      setPagination(result.pagination);
    } catch { /* 무시 */ }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchPosts(page);
  }, [page, fetchPosts]);

  const handleDelete = async (id: number) => {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    try {
      await deletePost(id);
      fetchPosts(page);
    } catch { /* 무시 */ }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-text-primary">포스트 관리</h1>
        <Button onClick={() => router.push("/admin/posts/new")}>
          새 포스트
        </Button>
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="animate-pulse h-16" />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-text-secondary">제목</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary hidden md:table-cell">카테고리</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary hidden md:table-cell">공개</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary hidden md:table-cell">작성일</th>
                <th className="text-right px-4 py-3 font-medium text-text-secondary">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {posts.map((post) => (
                <tr key={post.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-text-primary">{post.title}</td>
                  <td className="px-4 py-3 text-text-secondary hidden md:table-cell">
                    {post.category_name || "-"}
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${
                      post.visibility === "public"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}>
                      {post.visibility === "public" ? "공개" : "비공개"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-text-secondary hidden md:table-cell">
                    {formatDate(post.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => router.push(`/admin/posts/${post.slug}/edit`)}
                      className="text-primary hover:text-primary-hover text-sm mr-3"
                    >
                      수정
                    </button>
                    <button
                      onClick={() => handleDelete(post.id)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
              {posts.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-text-secondary">
                    포스트가 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* 페이지네이션 */}
      {pagination && pagination.total_pages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-4">
          <Button variant="secondary" onClick={() => setPage(page - 1)} disabled={page <= 1}>
            이전
          </Button>
          <span className="text-sm text-text-secondary">{page} / {pagination.total_pages}</span>
          <Button variant="secondary" onClick={() => setPage(page + 1)} disabled={page >= pagination.total_pages}>
            다음
          </Button>
        </div>
      )}
    </div>
  );
}
