import type { Metadata } from "next";
import "./globals.css";
import LayoutShell from "@/components/layout/LayoutShell";

export const metadata: Metadata = {
  title: "통합 블로그",
  description:
    "테크 블로그와 가족 데일리 사진을 하나의 플랫폼에서 관리하는 통합 블로그",
};

/** 루트 레이아웃 - 서버 컴포넌트, LayoutShell로 클라이언트 상태 위임 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-bg-primary text-text-primary">
        <LayoutShell>{children}</LayoutShell>
      </body>
    </html>
  );
}
