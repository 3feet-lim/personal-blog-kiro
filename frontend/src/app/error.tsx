/** 에러 바운더리 - 런타임 에러 발생 시 사용자 친화적 에러 페이지 표시 */
"use client";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  return (
    <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-center">
      {/* 에러 아이콘 */}
      <p className="text-6xl font-bold text-gray-200">!</p>

      {/* 안내 메시지 */}
      <h1 className="mt-4 text-xl font-semibold text-text-primary">
        문제가 발생했습니다
      </h1>
      <p className="mt-2 text-text-secondary">
        {error.message || "예기치 않은 오류가 발생했습니다. 다시 시도해 주세요."}
      </p>

      {/* 다시 시도 버튼 - reset() 호출로 현재 경로 재로드 */}
      <button
        onClick={reset}
        className="mt-6 bg-blue-500 text-white rounded-md px-4 py-2 hover:bg-blue-600 transition-colors"
      >
        다시 시도
      </button>
    </div>
  );
}
