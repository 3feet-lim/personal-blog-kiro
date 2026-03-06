/** 이미지 업로드 컴포넌트 - 드래그앤드롭 지원, 업로드 진행률 표시 */
"use client";

import { useState, useRef, useCallback } from "react";
import { uploadImage } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ImageUploadResponse } from "@/types";

interface ImageUploaderProps {
  /** 업로드 완료 콜백 - 마크다운 이미지 삽입 등에 활용 */
  onUpload?: (image: ImageUploadResponse) => void;
}

/** 드래그앤드롭 이미지 업로드 컴포넌트 */
export default function ImageUploader({ onUpload }: ImageUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploaded, setUploaded] = useState<ImageUploadResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /** 파일 업로드 처리 */
  const handleUpload = useCallback(
    async (file: File) => {
      // 이미지 형식 검증
      const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
      if (!allowedTypes.includes(file.type)) {
        setError("JPEG, PNG, GIF, WebP 형식만 지원합니다.");
        return;
      }

      setUploading(true);
      setError(null);
      setProgress(0);

      // 진행률 시뮬레이션 (실제 axios 진행률은 별도 설정 필요)
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      try {
        const result = await uploadImage(file);
        setProgress(100);
        setUploaded(result);
        onUpload?.(result);
      } catch {
        setError("이미지 업로드에 실패했습니다.");
      } finally {
        clearInterval(progressInterval);
        setUploading(false);
      }
    },
    [onUpload]
  );

  /** 드래그 이벤트 핸들러 */
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  /** 파일 선택 핸들러 */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  /** 초기화 */
  const reset = () => {
    setUploaded(null);
    setProgress(0);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="w-full">
      {/* 업로드 완료 상태 */}
      {uploaded ? (
        <div className="border border-gray-200 rounded-lg p-4 bg-green-50">
          <div className="flex items-center justify-between">
            <div className="text-sm">
              <p className="text-green-700 font-medium">업로드 완료</p>
              <p className="text-text-secondary mt-1 text-xs break-all">
                {uploaded.url}
              </p>
            </div>
            <button
              onClick={reset}
              className="text-sm text-primary hover:text-primary-hover"
            >
              다시 업로드
            </button>
          </div>
        </div>
      ) : (
        /* 드래그앤드롭 영역 */
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
            isDragging
              ? "border-primary bg-blue-50"
              : "border-gray-300 hover:border-gray-400"
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            onChange={handleFileChange}
            className="hidden"
          />

          {uploading ? (
            /* 업로드 진행률 */
            <div>
              <p className="text-sm text-text-secondary mb-2">업로드 중...</p>
              <div className="w-full bg-gray-200 rounded-full h-2 max-w-xs mx-auto">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-text-secondary mt-1">{progress}%</p>
            </div>
          ) : (
            <div>
              <svg
                className="w-10 h-10 text-gray-400 mx-auto mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="text-sm text-text-secondary">
                이미지를 드래그하거나 클릭하여 업로드
              </p>
              <p className="text-xs text-text-secondary mt-1">
                JPEG, PNG, GIF, WebP 지원
              </p>
            </div>
          )}
        </div>
      )}

      {/* 에러 메시지 */}
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
