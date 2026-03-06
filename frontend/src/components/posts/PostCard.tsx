/** 포스트 카드 컴포넌트 */

import Link from "next/link";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { PostListItem } from "@/types";

interface PostCardProps {
  /** 포스트 데이터 */
  post: PostListItem;
}

/** 포스트 목록에서 사용되는 카드 컴포넌트 */
export default function PostCard({ post }: PostCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <Link href={`/blog/${post.slug}`} className="block">
        <h2 className="text-lg font-semibold text-text-primary hover:text-primary transition-colors">
          {post.title}
        </h2>
        <div className="mt-2 flex items-center gap-3 text-sm text-text-secondary">
          <span>{post.author_name}</span>
          {post.category_name && (
            <>
              <span>·</span>
              <span>{post.category_name}</span>
            </>
          )}
          <span>·</span>
          <time dateTime={post.created_at}>{formatDate(post.created_at)}</time>
        </div>
        {/* 태그 표시 */}
        {post.tags && post.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
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
      </Link>
    </Card>
  );
}
