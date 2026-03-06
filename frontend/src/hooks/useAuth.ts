/** 인증 상태 관리 훅 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { getAccessToken, clearTokens } from "@/lib/auth";
import {
  login as apiLogin,
  logout as apiLogout,
  getMe,
  refreshToken as apiRefreshToken,
} from "@/lib/api";
import type { User, LoginRequest } from "@/types";

/** 인증 상태 및 관련 함수를 제공하는 훅 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /** 마운트 시 토큰이 있으면 사용자 정보 조회 */
  useEffect(() => {
    const fetchUser = async () => {
      const token = getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // 토큰으로 현재 사용자 정보 조회
        const currentUser = await getMe();
        setUser(currentUser);
      } catch {
        // 토큰 만료 시 리프레시 시도
        try {
          await apiRefreshToken();
          const currentUser = await getMe();
          setUser(currentUser);
        } catch {
          // 리프레시도 실패하면 토큰 정리 (만료된 세션)
          clearTokens();
          setUser(null);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  /** 로그인 - API 호출 후 사용자 정보 설정 */
  const login = useCallback(async (credentials: LoginRequest) => {
    await apiLogin(credentials);
    // 로그인 성공 시 사용자 정보 조회
    const currentUser = await getMe();
    setUser(currentUser);
  }, []);

  /** 로그아웃 - API 호출 후 상태 초기화 */
  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
  };
}
