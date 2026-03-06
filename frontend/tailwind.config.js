/** @type {import('tailwindcss').Config} */

/**
 * Tailwind CSS 설정
 * - 라이트 모드 전용 (다크 모드 미지원)
 * - 화이트 톤 기반 커스텀 색상 팔레트
 */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  // 다크 모드 비활성화 - 라이트 모드 전용
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        /* 액센트 색상 */
        primary: {
          DEFAULT: "#3B82F6",  // blue-500
          hover: "#2563EB",    // blue-600
        },
        /* 배경 색상 */
        "bg-primary": "#FFFFFF",
        "bg-secondary": "#F9FAFB",  // gray-50
        /* 텍스트 색상 */
        "text-primary": "#111827",   // gray-900
        "text-secondary": "#6B7280", // gray-500
        /* 보더 색상 */
        border: "#E5E7EB",           // gray-200
      },
    },
  },
  plugins: [],
};
