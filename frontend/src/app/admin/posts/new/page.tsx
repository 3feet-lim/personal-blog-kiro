/** 새 포스트 작성 페이지 */
import PostForm from "@/components/posts/PostForm";

export default function NewPostPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-text-primary mb-6">새 포스트 작성</h1>
      <PostForm />
    </div>
  );
}
