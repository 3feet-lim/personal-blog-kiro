/** 관리자 - 태그 관리 페이지 (목록, 생성, 수정, 삭제) */
"use client";

import { useState, useEffect, useCallback } from "react";
import { getTags, createTag, updateTag, deleteTag } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import type { Tag } from "@/types";

export default function AdminTagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchTags = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getTags();
      setTags(data);
    } catch { /* 무시 */ }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  /** 폼 초기화 */
  const resetForm = () => {
    setName("");
    setEditingTag(null);
    setShowForm(false);
  };

  /** 저장 (생성 또는 수정) */
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingTag) {
        await updateTag(editingTag.id, { name });
      } else {
        await createTag({ name });
      }
      resetForm();
      fetchTags();
    } catch { /* 무시 */ }
    setSaving(false);
  };

  /** 삭제 */
  const handleDelete = async (id: number) => {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    try {
      await deleteTag(id);
      fetchTags();
    } catch { /* 무시 */ }
  };

  /** 수정 모드 진입 */
  const startEdit = (tag: Tag) => {
    setEditingTag(tag);
    setName(tag.name);
    setShowForm(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-text-primary">태그 관리</h1>
        <Button onClick={() => { resetForm(); setShowForm(true); }}>
          새 태그
        </Button>
      </div>

      {/* 생성/수정 폼 */}
      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleSave} className="flex gap-3 items-end">
            <div className="flex-1">
              <Input
                id="tag-name"
                label="태그 이름"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={saving}>
                {saving ? "저장 중..." : editingTag ? "수정" : "생성"}
              </Button>
              <Button type="button" variant="secondary" onClick={resetForm}>
                취소
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* 태그 목록 */}
      {loading ? (
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-8 w-20 bg-gray-200 rounded-full animate-pulse" />
          ))}
        </div>
      ) : tags.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <div
              key={tag.id}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-gray-200 shadow-sm text-sm"
            >
              <span className="text-text-primary">{tag.name}</span>
              <span className="text-text-secondary text-xs">({tag.slug})</span>
              <button
                onClick={() => startEdit(tag)}
                className="text-primary hover:text-primary-hover text-xs ml-1"
              >
                수정
              </button>
              <button
                onClick={() => handleDelete(tag.id)}
                className="text-red-500 hover:text-red-700 text-xs"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      ) : (
        <Card>
          <p className="text-text-secondary text-center py-4">태그가 없습니다.</p>
        </Card>
      )}
    </div>
  );
}
