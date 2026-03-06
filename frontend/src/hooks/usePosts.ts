/** 포스트 데이터 관리 훅 */
"use client";

import { useState, useEffect } from "react";
import type { Post, PaginationMeta } from "@/types";

/** 포스트 목록 조회 훅 */
export function usePosts(page: number = 1, size: number = 10) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // TODO: API 연동
    setIsLoading(false);
  }, [page, size]);

  return { posts, pagination, isLoading, error };
}
