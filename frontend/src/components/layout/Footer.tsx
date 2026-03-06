/** 푸터 컴포넌트 */

/** 하단 푸터 */
export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white px-4 py-6 mt-auto">
      <div className="max-w-6xl mx-auto text-center text-sm text-text-secondary">
        <p>&copy; {new Date().getFullYear()} 통합 블로그. All rights reserved.</p>
      </div>
    </footer>
  );
}
