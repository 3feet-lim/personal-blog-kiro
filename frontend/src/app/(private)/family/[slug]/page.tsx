/** 가족 사진 상세 페이지 (비공개 - 인증 필요) */
"use client";

import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { getPostBySlug } from "@/lib/api";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { Post } from "@/types";

export default function FamilyPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /** 인증되지 않은 사용자는 로그인 페이지로 리다이렉트 */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  /** 포스트 데이터 가져오기 */
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchPost = async () => {
      setLoading(true);
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
  }, [slug, isAuthenticated]);

  if (authLoading || (!isAuthenticated && !authLoading)) {
    return (
      <div className="max-w-4xl mx-auto animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-4" />
        <div className="h-4 bg-gray-200 rounded w-1/3" />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-4" />
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-6" />
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-4 bg-gray-200 rounded" style={{ width: `${80 + Math.random() * 20}%` }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16">
        <p className="text-text-secondary">{error || "포스트를 찾을 수 없습니다."}</p>
        <Link href="/family" className="mt-4 inline-block text-primary hover:text-primary-hover">
          ← 가족 앨범으로 돌아가기
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* 제목 */}
      <h1 className="text-3xl font-bold text-text-primary">{post.title}</h1>

      {/* 메타 정보 */}
      <div className="mt-3 flex items-center gap-3 text-sm text-text-secondary">
        <span>{post.author.name}</span>
        <span>·</span>
        <time dateTime={post.created_at}>{formatDate(post.created_at)}</time>
        {post.category && (
          <>
            <span>·</span>
            <span>{post.category.name}</span>
          </>
        )}
      </div>

      {/* 태그 */}
      {post.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
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

      {/* 본문 */}
      <Card className="mt-6">
        <div className="prose max-w-none whitespace-pre-wrap">
          {post.content}
        </div>
      </Card>

      {/* 뒤로가기 */}
      <div className="mt-6">
        <Link href="/family" className="text-sm text-primary hover:text-primary-hover">
          ← 가족 앨범으로 돌아가기
        </Link>
      </div>
    </div>
  );
}
