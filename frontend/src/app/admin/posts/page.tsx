/** 관리자 - 포스트 관리 페이지 (목록, 생성, 수정, 삭제) */
"use client";

import { useState, useEffect, useCallback } from "react";
import { getPosts, createPost, updatePost, deletePost } from "@/lib/api";
import { getCategories } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { PostListItem, PostCreate, CategoryTree, PaginationMeta } from "@/types";

/** 포스트 생성/수정 모달 */
function PostFormModal({
  editingPost,
  categories,
  onSave,
  onClose,
}: {
  editingPost?: PostListItem | null;
  categories: CategoryTree[];
  onSave: (data: PostCreate, id?: number) => Promise<void>;
  onClose: () => void;
}) {
  const [title, setTitle] = useState(editingPost?.title || "");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<"public" | "private">(
    editingPost?.visibility || "public"
  );
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined);
  const [saving, setSaving] = useState(false);

  /** 카테고리 트리를 평탄화 */
  const flatCategories = flattenCategories(categories);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(
        { title, content, visibility, category_id: categoryId || null },
        editingPost?.id
      );
      onClose();
    } catch {
      // 에러는 부모에서 처리
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">
          {editingPost ? "포스트 수정" : "새 포스트 작성"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            id="title"
            label="제목"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-text-primary mb-1">
              내용 (마크다운)
            </label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={10}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
            />
          </div>
          <div className="flex gap-4">
            <div className="flex-1">
              <label htmlFor="visibility" className="block text-sm font-medium text-text-primary mb-1">
                공개 범위
              </label>
              <select
                id="visibility"
                value={visibility}
                onChange={(e) => setVisibility(e.target.value as "public" | "private")}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
              >
                <option value="public">공개</option>
                <option value="private">비공개 (가족)</option>
              </select>
            </div>
            <div className="flex-1">
              <label htmlFor="category" className="block text-sm font-medium text-text-primary mb-1">
                카테고리
              </label>
              <select
                id="category"
                value={categoryId || ""}
                onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
              >
                <option value="">선택 안함</option>
                {flatCategories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.prefix}{c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={onClose}>
              취소
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "저장 중..." : "저장"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

/** 카테고리 트리를 평탄화하여 select 옵션으로 사용 */
function flattenCategories(
  categories: CategoryTree[],
  depth = 0
): Array<{ id: number; name: string; prefix: string }> {
  const result: Array<{ id: number; name: string; prefix: string }> = [];
  for (const cat of categories) {
    result.push({ id: cat.id, name: cat.name, prefix: "─".repeat(depth) + (depth > 0 ? " " : "") });
    if (cat.children?.length) {
      result.push(...flattenCategories(cat.children, depth + 1));
    }
  }
  return result;
}

export default function AdminPostsPage() {
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [categories, setCategories] = useState<CategoryTree[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPost, setEditingPost] = useState<PostListItem | null>(null);

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
    getCategories().then(setCategories).catch(() => {});
  }, [page, fetchPosts]);

  /** 포스트 저장 (생성 또는 수정) */
  const handleSave = async (data: PostCreate, id?: number) => {
    if (id) {
      await updatePost(id, data);
    } else {
      await createPost(data);
    }
    setShowForm(false);
    setEditingPost(null);
    fetchPosts(page);
  };

  /** 포스트 삭제 */
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
        <Button onClick={() => { setEditingPost(null); setShowForm(true); }}>
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
                      onClick={() => { setEditingPost(post); setShowForm(true); }}
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

      {/* 포스트 생성/수정 모달 */}
      {showForm && (
        <PostFormModal
          editingPost={editingPost}
          categories={categories}
          onSave={handleSave}
          onClose={() => { setShowForm(false); setEditingPost(null); }}
        />
      )}
    </div>
  );
}
