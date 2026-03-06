/** 관리자 레이아웃 - 관리자 인증 확인 및 네비게이션 */
"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

/** 관리자 네비게이션 메뉴 항목 */
const adminMenuItems = [
  { href: "/admin/posts", label: "포스트" },
  { href: "/admin/categories", label: "카테고리" },
  { href: "/admin/tags", label: "태그" },
  { href: "/admin/users", label: "사용자" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading } = useAuth();

  /** 관리자가 아닌 경우 홈으로 리다이렉트 */
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || user?.role !== "admin")) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-text-secondary">로딩 중...</p>
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== "admin") return null;

  return (
    <div>
      {/* 관리자 네비게이션 */}
      <nav className="bg-white border-b border-gray-200 shadow-sm px-4 py-3">
        <div className="flex items-center gap-6">
          <h2 className="text-lg font-semibold text-text-primary">관리자</h2>
          <div className="flex gap-1">
            {adminMenuItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-3 py-1.5 rounded-md text-sm transition-colors",
                  pathname.startsWith(item.href)
                    ? "bg-primary text-white"
                    : "text-text-secondary hover:bg-gray-100"
                )}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* 콘텐츠 영역 */}
      <div className="p-4 md:p-6">{children}</div>
    </div>
  );
}
