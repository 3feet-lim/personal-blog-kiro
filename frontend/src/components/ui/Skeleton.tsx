/** 스켈레톤 로딩 컴포넌트 */

import { cn } from "@/lib/utils";

interface SkeletonProps {
  /** 추가 CSS 클래스 */
  className?: string;
}

/** 콘텐츠 로딩 중 표시되는 스켈레톤 플레이스홀더 */
export default function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-gray-200",
        className
      )}
    />
  );
}
