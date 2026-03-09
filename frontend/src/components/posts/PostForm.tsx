/** 포스트 작성/수정 폼 컴포넌트 - 에디터, 메타데이터 사이드바 */
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MarkdownEditor from "./MarkdownEditor";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { getCategories, getTags, createPost, updatePost, getPostBySlug } from "@/lib/api";
import type { CategoryTree, Tag, PostCreate, Visibility } from "@/types";

interface PostFormProps {
  /** 수정 모드일 때 기존 포스트 slug */
  editSlug?: string;
}

/** 카테고리 트리를 평탄화 */
function flattenCategories(
  categories: CategoryTree[],
  depth = 0
): Array<{ id: number; name: string; prefix: string }> {
  const result: Array<{ id: number; name: string; prefix: string }> = [];
  for (const cat of categories) {
    result.push({ id: cat.id, name: cat.name, prefix: "─".repeat(depth) + (depth > 0 ? " " : "") });
    if (cat.children?.length) result.push(...flattenCategories(cat.children, depth + 1));
  }
  return result;
}

export default function PostForm({ editSlug }: PostFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<Visibility>("public");
  const [categoryId, setCategoryId] = useState<number | undefined>();
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [categories, setCategories] = useState<CategoryTree[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [saving, setSaving] = useState(false);
  const [editPostId, setEditPostId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  /** 카테고리, 태그 목록 로드 + 수정 모드 시 기존 데이터 로드 */
  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
    getTags().then(setTags).catch(() => {});

    if (editSlug) {
      getPostBySlug(editSlug).then((post) => {
        setTitle(post.title);
        setContent(post.content);
        setVisibility(post.visibility);
        setCategoryId(post.category?.id);
        setSelectedTagIds(post.tags?.map((t) => t.id) ?? []);
        setEditPostId(post.id);
      }).catch(() => setError("포스트를 불러올 수 없습니다."));
    }
  }, [editSlug]);

  const flatCats = flattenCategories(categories);

  const toggleTag = (tagId: number) => {
    setSelectedTagIds((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  };

  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) {
      setError("제목과 내용을 입력해주세요.");
      return;
    }

    setSaving(true);
    setError(null);
    try {
      const data: PostCreate = {
        title: title.trim(),
        content,
        visibility,
        category_id: categoryId ?? null,
        tag_ids: selectedTagIds,
      };

      if (editPostId) {
        await updatePost(editPostId, data);
      } else {
        await createPost(data);
      }
      router.push("/admin/posts");
    } catch {
      setError("저장에 실패했습니다.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* 메인: 제목 + 에디터 */}
      <div className="flex-1 space-y-4">
        <Input
          id="title"
          label="제목"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="포스트 제목을 입력하세요"
          required
        />
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1">내용</label>
          <MarkdownEditor value={content} onChange={setContent} />
        </div>
      </div>

      {/* 사이드바: 메타데이터 */}
      <div className="w-full lg:w-72 space-y-4">
        {/* 공개 범위 */}
        <div>
          <label htmlFor="visibility" className="block text-sm font-medium text-text-primary mb-1">
            공개 범위
          </label>
          <select
            id="visibility"
            value={visibility}
            onChange={(e) => setVisibility(e.target.value as Visibility)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
          >
            <option value="public">공개</option>
            <option value="private">비공개 (가족)</option>
          </select>
        </div>

        {/* 카테고리 */}
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-text-primary mb-1">
            카테고리
          </label>
          <select
            id="category"
            value={categoryId ?? ""}
            onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : undefined)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
          >
            <option value="">선택 안함</option>
            {flatCats.map((c) => (
              <option key={c.id} value={c.id}>
                {c.prefix}{c.name}
              </option>
            ))}
          </select>
        </div>

        {/* 태그 */}
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1">태그</label>
          <div className="flex flex-wrap gap-1.5 p-2 border border-gray-300 rounded-md min-h-[40px]">
            {tags.length === 0 && (
              <span className="text-xs text-gray-400">등록된 태그가 없습니다</span>
            )}
            {tags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => toggleTag(tag.id)}
                className={cn(
                  "px-2 py-0.5 text-xs rounded-full border transition-colors",
                  selectedTagIds.includes(tag.id)
                    ? "bg-primary text-white border-primary"
                    : "bg-gray-100 text-gray-600 border-gray-200 hover:border-gray-400"
                )}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {/* 저장 버튼 */}
        <Button onClick={handleSubmit} disabled={saving} className="w-full">
          {saving ? "저장 중..." : editPostId ? "수정" : "발행"}
        </Button>
        <Button
          variant="secondary"
          onClick={() => router.push("/admin/posts")}
          className="w-full"
        >
          취소
        </Button>
      </div>
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(" ");
}
