/** 포스트 상세 로딩 스켈레톤 UI - 제목, 메타데이터, 본문 플레이스홀더 */

export default function BlogPostLoading() {
  return (
    <div className="max-w-4xl mx-auto animate-pulse">
      {/* 제목 플레이스홀더 (큰 사이즈) */}
      <div className="h-8 bg-gray-200 rounded w-4/5" />
      <div className="h-8 bg-gray-200 rounded w-3/5 mt-2" />

      {/* 메타 정보 플레이스홀더 (작성자, 날짜, 카테고리) */}
      <div className="mt-4 flex items-center gap-3">
        <div className="h-4 bg-gray-200 rounded w-20" />
        <div className="h-4 bg-gray-200 rounded w-24" />
        <div className="h-4 bg-gray-200 rounded w-16" />
      </div>

      {/* 태그 플레이스홀더 */}
      <div className="mt-4 flex gap-2">
        <div className="h-6 bg-gray-100 rounded-full w-14" />
        <div className="h-6 bg-gray-100 rounded-full w-18" />
        <div className="h-6 bg-gray-100 rounded-full w-12" />
      </div>

      {/* 구분선 */}
      <div className="mt-6 border-t border-gray-200" />

      {/* 본문 플레이스홀더 (다양한 너비의 줄) */}
      <div className="mt-6 space-y-3">
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-4/6" />
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
        <div className="h-4 bg-gray-200 rounded w-2/3" />
      </div>
    </div>
  );
}
