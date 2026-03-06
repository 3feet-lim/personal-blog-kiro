/** 관리자 - 사용자 관리 페이지 (목록, 생성, 비활성화) */
"use client";

import { useState, useEffect, useCallback } from "react";
import { getUsers, createUser, deactivateUser } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { User, UserRole } from "@/types";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // 생성 폼 상태
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<UserRole>("family_member");
  const [saving, setSaving] = useState(false);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } catch { /* 무시 */ }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  /** 폼 초기화 */
  const resetForm = () => {
    setEmail("");
    setPassword("");
    setName("");
    setRole("family_member");
    setShowForm(false);
  };

  /** 사용자 생성 */
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createUser({ email, password, name, role });
      resetForm();
      fetchUsers();
    } catch { /* 무시 */ }
    setSaving(false);
  };

  /** 사용자 비활성화 */
  const handleDeactivate = async (id: number) => {
    if (!confirm("정말 비활성화하시겠습니까?")) return;
    try {
      await deactivateUser(id);
      fetchUsers();
    } catch { /* 무시 */ }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-text-primary">사용자 관리</h1>
        <Button onClick={() => { resetForm(); setShowForm(true); }}>
          새 사용자
        </Button>
      </div>

      {/* 생성 폼 */}
      {showForm && (
        <Card className="mb-4">
          <h2 className="text-lg font-semibold mb-3">새 사용자 생성</h2>
          <form onSubmit={handleCreate} className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Input
                id="user-name"
                label="이름"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
              <Input
                id="user-email"
                label="이메일"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Input
                id="user-password"
                label="비밀번호"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <div>
                <label htmlFor="user-role" className="block text-sm font-medium text-text-primary mb-1">
                  역할
                </label>
                <select
                  id="user-role"
                  value={role}
                  onChange={(e) => setRole(e.target.value as UserRole)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary focus:outline-none"
                >
                  <option value="family_member">가족 구성원</option>
                  <option value="admin">관리자</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="secondary" onClick={resetForm}>
                취소
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "생성 중..." : "생성"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* 사용자 목록 */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="animate-pulse h-14" />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-text-secondary">이름</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary hidden md:table-cell">이메일</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary">역할</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary hidden md:table-cell">상태</th>
                <th className="text-left px-4 py-3 font-medium text-text-secondary hidden md:table-cell">가입일</th>
                <th className="text-right px-4 py-3 font-medium text-text-secondary">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-text-primary">{user.name}</td>
                  <td className="px-4 py-3 text-text-secondary hidden md:table-cell">{user.email}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${
                      user.role === "admin"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-700"
                    }`}>
                      {user.role === "admin" ? "관리자" : "가족"}
                    </span>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${
                      user.is_active
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }`}>
                      {user.is_active ? "활성" : "비활성"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-text-secondary hidden md:table-cell">
                    {formatDate(user.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {user.is_active && (
                      <button
                        onClick={() => handleDeactivate(user.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        비활성화
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-text-secondary">
                    사용자가 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
