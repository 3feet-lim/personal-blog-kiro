/** 카테고리 트리 컴포넌트 */
"use client";

import Link from "next/link";
import type { CategoryTree as CategoryTreeType } from "@/types";

interface CategoryTreeProps {
  /** 카테고리 트리 데이터 */
  categories: CategoryTreeType[];
}

/** 재귀적 카테고리 트리 렌더링 컴포넌트 */
export default function CategoryTree({ categories }: CategoryTreeProps) {
  if (categories.length === 0) {
    return (
      <p className="text-sm text-text-secondary px-3 py-2">
        카테고리가 없습니다.
      </p>
    );
  }

  return (
    <ul className="space-y-1">
      {categories.map((category) => (
        <CategoryItem key={category.id} category={category} />
      ))}
    </ul>
  );
}

/** 개별 카테고리 아이템 (재귀 렌더링) */
function CategoryItem({ category }: { category: CategoryTreeType }) {
  return (
    <li>
      <Link
        href={`/category/${category.slug}`}
        className="block px-3 py-1.5 rounded-md text-sm text-text-primary hover:bg-gray-100 transition-colors"
      >
        {category.name}
      </Link>
      {/* 하위 카테고리 재귀 렌더링 */}
      {category.children && category.children.length > 0 && (
        <ul className="ml-4 space-y-1">
          {category.children.map((child) => (
            <CategoryItem key={child.id} category={child} />
          ))}
        </ul>
      )}
    </li>
  );
}
