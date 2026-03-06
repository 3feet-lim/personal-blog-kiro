/** 레이아웃 셸 - 사이드바 상태를 관리하는 클라이언트 래퍼 컴포넌트 */
"use client";

import { useState, useCallback, useEffect } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";
import Footer from "./Footer";

interface LayoutShellProps {
  children: React.ReactNode;
}

/** 사이드바 + 헤더 + 메인 콘텐츠 + 푸터를 통합 관리하는 셸 */
export default function LayoutShell({ children }: LayoutShellProps) {
  /** 사이드바 열림/닫힘 상태 (데스크톱: 기본 열림, 모바일: 기본 닫힘) */
  const [sidebarOpen, setSidebarOpen] = useState(false);
  /** 현재 데스크톱 뷰포트인지 여부 */
  const [isDesktop, setIsDesktop] = useState(false);

  /** 화면 크기에 따라 사이드바 초기 상태 및 데스크톱 여부 설정 */
  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 768px)");
    setIsDesktop(mediaQuery.matches);
    setSidebarOpen(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setIsDesktop(e.matches);
      setSidebarOpen(e.matches);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  /** 사이드바 토글 */
  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  /** 사이드바 닫기 (모바일 오버레이 클릭 시) */
  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* 헤더 - 상단 고정 */}
      <Header onToggleSidebar={toggleSidebar} />

      {/* 사이드바 + 메인 콘텐츠 영역 */}
      <div className="flex flex-1 relative">
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

        {/* 메인 콘텐츠 - 데스크톱에서 사이드바 열림 시 마진으로 공간 확보 */}
        <main
          className="flex-1 min-w-0 transition-all duration-300 ease-in-out"
          style={{
            marginLeft: isDesktop && sidebarOpen ? "256px" : "0px",
          }}
        >
          <div className="px-4 md:px-8 py-6">{children}</div>
        </main>
      </div>

      {/* 푸터 */}
      <Footer />
    </div>
  );
}
