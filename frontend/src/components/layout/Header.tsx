/** 헤더 컴포넌트 - 로고, 햄버거 메뉴, 인증 상태 표시 */
"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

interface HeaderProps {
  /** 사이드바 토글 콜백 */
  onToggleSidebar?: () => void;
}

/** 상단 헤더 컴포넌트 */
export default function Header({ onToggleSidebar }: HeaderProps) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  /** 로그아웃 처리 */
  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // 로그아웃 실패 시에도 UI는 초기화됨
    }
  };

  return (
    <header className="sticky top-0 z-30 h-[53px] bg-white border-b border-gray-200 shadow-sm px-4 flex items-center justify-between">
      {/* 왼쪽: 햄버거 메뉴 + 로고 */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-md hover:bg-gray-100 transition-colors"
          aria-label="사이드바 토글"
        >
          {/* 햄버거 아이콘 */}
          <svg
            className="w-5 h-5 text-text-primary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <Link href="/" className="text-xl font-bold text-text-primary">
          통합 블로그
        </Link>
      </div>

      {/* 오른쪽: 인증 상태에 따른 UI */}
      <nav className="flex items-center gap-3">
        {isLoading ? (
          /* 로딩 중 플레이스홀더 */
          <div className="h-4 w-16 bg-gray-100 rounded animate-pulse" />
        ) : isAuthenticated && user ? (
          /* 로그인 상태: 사용자 이름 + 로그아웃 버튼 */
          <div className="flex items-center gap-3">
            <span className="text-sm text-text-secondary">{user.name}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              로그아웃
            </button>
          </div>
        ) : (
          /* 비로그인 상태: 로그인 링크 */
          <Link
            href="/login"
            className="text-sm text-primary hover:text-primary-hover transition-colors"
          >
            로그인
          </Link>
        )}
      </nav>
    </header>
  );
}
