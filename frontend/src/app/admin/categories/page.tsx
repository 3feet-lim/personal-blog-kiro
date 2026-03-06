/** 관리자 - 카테고리 관리 페이지 */
"use client";

import { useState, useEffect, useCallback } from "react";
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import type { CategoryTree, CategoryCreate } from "@/types";

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState<CategoryTree[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [parentId, setParentId] = useState<number | undefined>(undefined);
  const [saving, setSaving] = useState(false);

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getCategories();
      setCategories(data);
    } catch { /* 무시 */ }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  /** 카테고리 트리를 평탄화 */
  const flatCategories = flattenCategories(categories);

  /** 폼 초기화 */
  const resetForm = () => {
    setName("");
    setParentId(undefined);
    setEditingId(null);
    setShowForm(false);
  };

  /** 저장 (생성 또는 수정) */
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data: CategoryCreate = { name, parent_id: parentId || null };
      if (editingId) {
        await updateCategory(editingId, data);
      } else {
        await createCategory(data);
      }
      resetForm();
      fetchCategories();
    } catch { /* 무시 */ }
    setSaving(false);
  };

  /** 삭제 */
  const handleDelete = async (id: number) => {
    if (!confirm("정말 삭제하시겠습니까? 하위 카테고리도 함께 삭제됩니다.")) return;
    try {
      await deleteCategory(id);
      fetchCategories();
    } catch { /* 무시 */ }
  };

  /** 수정 모드 진입 */
  const startEdit = (cat: { id: number; name: string; parent_id?: number | null }) => {
    setEditingId(cat.id);
    setName(cat.name);
    setParentId(cat.parent_id || undefined);
    setShowForm(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-text-primary">카테고리 관리</h1>
        <Button onClick={() => { resetForm(); setShowForm(true); }}>
          새 카테고리
        </Button>
      </div>

      {/* 생성/수정 폼 */}
      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSave} className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[200px]">
              <Input
                id="cat-name"
                label="카테고리 이름"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="min-w-[200px]">
              <label htmlFor="parent" className="block text-sm font-medium text-text-primary mb-1">
                상위 카테고리
              </label>
              <select
                id="parent"
                value={parentId || ""}
                onChange={(e) => setParentId(e.target.value ? Number(e.target.value) : undefined)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
              >
                <option value="">없음 (최상위)</option>
                {flatCategories
                  .filter((c) => c.id !== editingId)
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.prefix}{c.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={saving}>
                {saving ? "저장 중..." : editingId ? "수정" : "생성"}
              </Button>
              <Button type="button" variant="secondary" onClick={resetForm}>
                취소
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* 카테고리 목록 */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-pulse h-12" />
          ))}
        </div>
      ) : categories.length > 0 ? (
        <Card className="p-0 overflow-hidden">
          <CategoryList
            categories={categories}
            depth={0}
            onEdit={startEdit}
            onDelete={handleDelete}
          />
        </Card>
      ) : (
        <Card>
          <p className="text-text-secondary text-center py-4">카테고리가 없습니다.</p>
        </Card>
      )}
    </div>
  );
}

/** 재귀적 카테고리 목록 렌더링 */
function CategoryList({
  categories,
  depth,
  onEdit,
  onDelete,
}: {
  categories: CategoryTree[];
  depth: number;
  onEdit: (cat: { id: number; name: string; parent_id?: number | null }) => void;
  onDelete: (id: number) => void;
}) {
  return (
    <ul className="divide-y divide-gray-200">
      {categories.map((cat) => (
        <li key={cat.id}>
          <div className="flex items-center justify-between px-4 py-3 hover:bg-gray-50">
            <span
              className="text-sm text-text-primary"
              style={{ paddingLeft: `${depth * 20}px` }}
            >
              {depth > 0 && <span className="text-gray-400 mr-1">└</span>}
              {cat.name}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => onEdit({ id: cat.id, name: cat.name })}
                className="text-primary hover:text-primary-hover text-sm"
              >
                수정
              </button>
              <button
                onClick={() => onDelete(cat.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                삭제
              </button>
            </div>
          </div>
          {cat.children?.length > 0 && (
            <CategoryList
              categories={cat.children}
              depth={depth + 1}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          )}
        </li>
      ))}
    </ul>
  );
}

/** 카테고리 트리를 평탄화 */
function flattenCategories(
  categories: CategoryTree[],
  depth = 0
): Array<{ id: number; name: string; prefix: string; parent_id?: number | null }> {
  const result: Array<{ id: number; name: string; prefix: string; parent_id?: number | null }> = [];
  for (const cat of categories) {
    result.push({ id: cat.id, name: cat.name, prefix: "─".repeat(depth) + (depth > 0 ? " " : "") });
    if (cat.children?.length) {
      result.push(...flattenCategories(cat.children, depth + 1));
    }
  }
  return result;
}
