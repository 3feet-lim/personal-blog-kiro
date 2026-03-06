/** 홈페이지 - 최신 포스트 미리보기, 카테고리 소개 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import PostCard from "@/components/posts/PostCard";
import Card from "@/components/ui/Card";
import { getPosts, getCategories } from "@/lib/api";
import type { PostListItem, CategoryTree } from "@/types";

/** 최신 포스트 표시 개수 */
const RECENT_POSTS_SIZE = 6;

export default function HomePage() {
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [categories, setCategories] = useState<CategoryTree[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [postsRes, categoriesRes] = await Promise.allSettled([
          getPosts({ page: 1, size: RECENT_POSTS_SIZE }),
          getCategories(),
        ]);

        if (postsRes.status === "fulfilled") {
          setPosts(postsRes.value.data);
        }
        if (categoriesRes.status === "fulfilled") {
          setCategories(categoriesRes.value);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <div className="max-w-6xl mx-auto">
      {/* 히어로 섹션 */}
      <section className="py-8 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-text-primary">
          통합 블로그
        </h1>
        <p className="mt-3 text-lg text-text-secondary max-w-2xl mx-auto">
          테크 블로그와 가족 데일리 사진을 하나의 플랫폼에서 관리합니다.
        </p>
      </section>

      {/* 최신 포스트 섹션 */}
      <section className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-text-primary">
            최신 포스트
          </h2>
          <Link
            href="/blog"
            className="text-sm text-primary hover:text-primary-hover transition-colors"
          >
            전체 보기 →
          </Link>
        </div>

        {loading ? (
          /* 로딩 스켈레톤 */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-3" />
                <div className="h-4 bg-gray-100 rounded w-1/2" />
              </Card>
            ))}
          </div>
        ) : posts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <Card>
            <p className="text-text-secondary text-center py-4">
              아직 작성된 포스트가 없습니다.
            </p>
          </Card>
        )}
      </section>

      {/* 카테고리 섹션 */}
      <section className="mt-12 mb-8">
        <h2 className="text-xl font-semibold text-text-primary mb-4">
          카테고리
        </h2>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-2/3" />
              </Card>
            ))}
          </div>
        ) : categories.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {categories.map((category) => (
              <Link key={category.id} href={`/category/${category.slug}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <h3 className="font-medium text-text-primary">
                    {category.name}
                  </h3>
                  {/* 하위 카테고리가 있으면 표시 */}
                  {category.children.length > 0 && (
                    <p className="mt-1 text-sm text-text-secondary">
                      {category.children.map((c) => c.name).join(", ")}
                    </p>
                  )}
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card>
            <p className="text-text-secondary text-center py-4">
              등록된 카테고리가 없습니다.
            </p>
          </Card>
        )}
      </section>
    </div>
  );
}
