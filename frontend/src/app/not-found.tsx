/** 404 페이지 - 존재하지 않는 페이지 접근 시 표시 */

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-center">
      {/* 404 코드 */}
      <p className="text-6xl font-bold text-gray-200">404</p>

      {/* 안내 메시지 */}
      <h1 className="mt-4 text-xl font-semibold text-text-primary">
        페이지를 찾을 수 없습니다
      </h1>
      <p className="mt-2 text-text-secondary">
        요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.
      </p>

      {/* 홈으로 돌아가기 링크 */}
      <Link
        href="/"
        className="mt-6 text-primary hover:text-primary-hover transition-colors"
      >
        ← 홈으로 돌아가기
      </Link>
    </div>
  );
}
