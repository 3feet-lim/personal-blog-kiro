/** 카드 컴포넌트 */

import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

/** 재사용 가능한 카드 컴포넌트 */
export default function Card({ className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "bg-white rounded-lg border border-gray-200 shadow-sm p-4",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
