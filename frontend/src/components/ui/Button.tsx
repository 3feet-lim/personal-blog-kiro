/** 기본 버튼 컴포넌트 */

import { type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

/** 버튼 변형(variant) 타입 */
type ButtonVariant = "primary" | "secondary";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** 버튼 스타일 변형 */
  variant?: ButtonVariant;
}

/** 버튼 변형별 스타일 매핑 */
const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-primary text-white hover:bg-primary-hover",
  secondary:
    "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50",
};

/** 재사용 가능한 버튼 컴포넌트 */
export default function Button({
  variant = "primary",
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
