/** 마크다운 에디터 - 툴바, 실시간 프리뷰, 이미지 업로드 연동 */
"use client";

import { useState, useRef, useCallback } from "react";
import MarkdownRenderer from "./MarkdownRenderer";
import { uploadImage } from "@/lib/api";
import { cn } from "@/lib/utils";

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
}

/** 툴바 버튼 정의 */
const toolbarItems = [
  { label: "B", title: "볼드", prefix: "**", suffix: "**" },
  { label: "I", title: "이탤릭", prefix: "_", suffix: "_" },
  { label: "H1", title: "제목1", prefix: "# ", suffix: "" },
  { label: "H2", title: "제목2", prefix: "## ", suffix: "" },
  { label: "H3", title: "제목3", prefix: "### ", suffix: "" },
  { label: "🔗", title: "링크", prefix: "[", suffix: "](url)" },
  { label: "<>", title: "코드", prefix: "`", suffix: "`" },
  { label: "```", title: "코드블록", prefix: "```\n", suffix: "\n```" },
  { label: "❝", title: "인용", prefix: "> ", suffix: "" },
  { label: "•", title: "리스트", prefix: "- ", suffix: "" },
] as const;

export default function MarkdownEditor({ value, onChange }: MarkdownEditorProps) {
  const [showPreview, setShowPreview] = useState(false);
  const [uploading, setUploading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /** 툴바 버튼 클릭 시 선택 영역에 마크다운 문법 삽입 */
  const insertMarkdown = useCallback(
    (prefix: string, suffix: string) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const selected = value.slice(start, end);
      const newText = value.slice(0, start) + prefix + selected + suffix + value.slice(end);
      onChange(newText);

      // 커서 위치 복원
      requestAnimationFrame(() => {
        textarea.focus();
        const cursorPos = start + prefix.length + selected.length;
        textarea.setSelectionRange(cursorPos, cursorPos);
      });
    },
    [value, onChange]
  );

  /** 이미지 파일 업로드 후 마크다운에 삽입 */
  const handleImageUpload = useCallback(
    async (file: File) => {
      const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
      if (!allowedTypes.includes(file.type)) return;

      setUploading(true);
      try {
        const result = await uploadImage(file);
        const textarea = textareaRef.current;
        const pos = textarea?.selectionStart ?? value.length;
        const imageMarkdown = `![image](${result.url})`;
        const newText = value.slice(0, pos) + imageMarkdown + value.slice(pos);
        onChange(newText);
      } catch {
        // 업로드 실패 무시
      } finally {
        setUploading(false);
      }
    },
    [value, onChange]
  );

  /** 에디터 영역에 이미지 드롭/붙여넣기 */
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file?.type.startsWith("image/")) handleImageUpload(file);
    },
    [handleImageUpload]
  );

  const handlePaste = useCallback(
    (e: React.ClipboardEvent) => {
      const file = e.clipboardData.files[0];
      if (file?.type.startsWith("image/")) {
        e.preventDefault();
        handleImageUpload(file);
      }
    },
    [handleImageUpload]
  );

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden">
      {/* 툴바 */}
      <div className="flex items-center gap-1 px-2 py-1.5 bg-gray-50 border-b border-gray-300 flex-wrap">
        {toolbarItems.map((item) => (
          <button
            key={item.title}
            type="button"
            title={item.title}
            onClick={() => insertMarkdown(item.prefix, item.suffix)}
            className="px-2 py-1 text-xs font-mono rounded hover:bg-gray-200 text-gray-700"
          >
            {item.label}
          </button>
        ))}
        <span className="mx-1 text-gray-300">|</span>
        <label
          className={cn(
            "px-2 py-1 text-xs rounded cursor-pointer hover:bg-gray-200 text-gray-700",
            uploading && "opacity-50 pointer-events-none"
          )}
          title="이미지 업로드"
        >
          🖼️
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleImageUpload(file);
              e.target.value = "";
            }}
          />
        </label>
        {uploading && <span className="text-xs text-gray-500">업로드 중...</span>}

        {/* 프리뷰 토글 */}
        <div className="ml-auto">
          <button
            type="button"
            onClick={() => setShowPreview(!showPreview)}
            className={cn(
              "px-3 py-1 text-xs rounded",
              showPreview ? "bg-primary text-white" : "hover:bg-gray-200 text-gray-700"
            )}
          >
            {showPreview ? "에디터" : "프리뷰"}
          </button>
        </div>
      </div>

      {/* 에디터 / 프리뷰 */}
      {showPreview ? (
        <div className="p-4 min-h-[400px] bg-white overflow-y-auto">
          {value ? (
            <MarkdownRenderer content={value} />
          ) : (
            <p className="text-gray-400 text-sm">프리뷰할 내용이 없습니다.</p>
          )}
        </div>
      ) : (
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onPaste={handlePaste}
          placeholder="마크다운으로 내용을 작성하세요... (이미지 드래그앤드롭 또는 붙여넣기 가능)"
          className="w-full min-h-[400px] p-4 text-sm font-mono resize-y focus:outline-none"
        />
      )}
    </div>
  );
}
