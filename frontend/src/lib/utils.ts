/** 공통 유틸리티 함수 */

/** 날짜를 한국어 형식으로 포맷 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/** CSS 클래스 이름 결합 (falsy 값 필터링) */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(" ");
}
