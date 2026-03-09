/** 포스트 수정 페이지 */
"use client";

import { use } from "react";
import PostForm from "@/components/posts/PostForm";

export default function EditPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);

  return (
    <div>
      <h1 className="text-2xl font-bold text-text-primary mb-6">포스트 수정</h1>
      <PostForm editSlug={slug} />
    </div>
  );
}
