/** 접이식 사이드바 컴포넌트 - 카테고리 트리, 네비게이션 */
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { getCategories } from "@/lib/api";
import CategoryTree from "@/components/categories/CategoryTree";
import type { CategoryTree as CategoryTreeType } from "@/types";

interface SidebarProps {
  /** 사이드바 열림 상태 */
  isOpen: boolean;
  /** 사이드바 닫기 콜백 */
  onClose: () => void;
}

/** 접이식 사이드바 - 카테고리 트리 네비게이션 포함 */
export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [categories, setCategories] = useState<CategoryTreeType[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  /** 마운트 시 카테고리 데이터 페칭 */
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await getCategories();
        setCategories(data);
      } catch {
        // API 연결 실패 시 빈 배열 유지
        setCategories([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return (
    <>
      {/* 모바일 오버레이 배경 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* 사이드바 본체 - 헤더 아래 고정 */}
      <aside
        className={cn(
          "fixed top-[53px] left-0 z-50 h-[calc(100vh-53px)]",
          "bg-white border-r border-gray-200",
          "transition-all duration-300 ease-in-out",
          "overflow-y-auto overflow-x-hidden",
          isOpen ? "w-64" : "w-0",
          /* 데스크톱에서는 z-index를 낮춰서 콘텐츠 위에 뜨지 않도록 */
          "md:z-10"
        )}
      >
        <nav className="p-4 w-64">
          {/* 섹션 네비게이션 */}
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
              섹션
            </h3>
            <ul className="space-y-1">
              <li>
                <Link
                  href="/blog"
                  className="block px-3 py-2 rounded-md text-sm text-text-primary hover:bg-gray-100 transition-colors"
                >
                  테크 블로그
                </Link>
              </li>
              <li>
                <Link
                  href="/family"
                  className="block px-3 py-2 rounded-md text-sm text-text-primary hover:bg-gray-100 transition-colors"
                >
                  가족 앨범
                </Link>
              </li>
            </ul>
          </div>

          {/* 카테고리 트리 */}
          <div>
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
              카테고리
            </h3>
            {isLoading ? (
              /* 로딩 스켈레톤 */
              <div className="space-y-2 px-3">
                <div className="h-4 bg-gray-100 rounded animate-pulse" />
                <div className="h-4 bg-gray-100 rounded animate-pulse w-3/4" />
                <div className="h-4 bg-gray-100 rounded animate-pulse w-1/2" />
              </div>
            ) : (
              <CategoryTree categories={categories} />
            )}
          </div>
        </nav>
      </aside>
    </>
  );
}
