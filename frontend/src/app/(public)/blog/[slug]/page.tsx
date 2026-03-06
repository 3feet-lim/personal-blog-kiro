/** 블로그 포스트 상세 페이지 - 마크다운 렌더링, 태그 표시 */
"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { getPostBySlug } from "@/lib/api";
import MarkdownRenderer from "@/components/posts/MarkdownRenderer";
import { formatDate } from "@/lib/utils";
import type { Post } from "@/types";

export default function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const data = await getPostBySlug(slug);
        setPost(data);
      } catch {
        setError("포스트를 불러올 수 없습니다.");
      } finally {
        setLoading(false);
      }
    };
    fetchPost();
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-4/5 mb-2" />
        <div className="h-8 bg-gray-200 rounded w-3/5" />
        <div className="mt-4 flex gap-3">
          <div className="h-4 bg-gray-200 rounded w-20" />
          <div className="h-4 bg-gray-200 rounded w-24" />
        </div>
        <div className="mt-6 border-t border-gray-200" />
        <div className="mt-6 space-y-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded" style={{ width: `${70 + Math.random() * 30}%` }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16">
        <p className="text-text-secondary">{error || "포스트를 찾을 수 없습니다."}</p>
        <Link href="/blog" className="mt-4 inline-block text-primary hover:text-primary-hover">
          ← 블로그 목록으로 돌아가기
        </Link>
      </div>
    );
  }

  return (
    <article className="max-w-4xl mx-auto">
      {/* 제목 */}
      <h1 className="text-3xl font-bold text-text-primary">{post.title}</h1>

      {/* 메타 정보 */}
      <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-text-secondary">
        <span>{post.author.name}</span>
        <span>·</span>
        <time dateTime={post.created_at}>{formatDate(post.created_at)}</time>
        {post.category && (
          <>
            <span>·</span>
            <Link
              href={`/category/${post.category.slug}`}
              className="text-primary hover:text-primary-hover"
            >
              {post.category.name}
            </Link>
          </>
        )}
      </div>

      {/* 태그 */}
      {post.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {post.tags.map((tag) => (
            <Link
              key={tag.id}
              href={`/tag/${tag.slug}`}
              className="inline-block px-2 py-0.5 text-xs rounded-full bg-gray-100 text-text-secondary hover:bg-gray-200 transition-colors"
            >
              {tag.name}
            </Link>
          ))}
        </div>
      )}

      {/* 구분선 */}
      <hr className="mt-6 border-gray-200" />

      {/* 본문 (마크다운 렌더링) */}
      <div className="mt-6">
        <MarkdownRenderer content={post.content} />
      </div>

      {/* 하단 네비게이션 */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <Link href="/blog" className="text-sm text-primary hover:text-primary-hover">
          ← 블로그 목록으로 돌아가기
        </Link>
      </div>
    </article>
  );
}
