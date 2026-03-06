/** 블로그 목록 로딩 스켈레톤 UI - 카드 형태 플레이스홀더 */

export default function BlogListLoading() {
  return (
    <div className="max-w-6xl mx-auto">
      {/* 제목 스켈레톤 */}
      <div className="h-7 bg-gray-200 rounded w-24 mb-6 animate-pulse" />

      {/* 포스트 카드 스켈레톤 목록 */}
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 animate-pulse"
          >
            {/* 제목 플레이스홀더 */}
            <div className="h-5 bg-gray-200 rounded w-3/4" />

            {/* 메타 정보 플레이스홀더 (작성자, 날짜, 카테고리) */}
            <div className="mt-3 flex items-center gap-3">
              <div className="h-4 bg-gray-200 rounded w-16" />
              <div className="h-4 bg-gray-200 rounded w-20" />
              <div className="h-4 bg-gray-200 rounded w-24" />
            </div>

            {/* 태그 플레이스홀더 */}
            <div className="mt-3 flex gap-1">
              <div className="h-5 bg-gray-100 rounded-full w-12" />
              <div className="h-5 bg-gray-100 rounded-full w-16" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
