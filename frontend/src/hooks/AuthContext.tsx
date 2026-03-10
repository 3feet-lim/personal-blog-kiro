/** 인증 상태를 앱 전체에서 공유하는 Context */
"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { getAccessToken, clearTokens } from "@/lib/auth";
import {
  login as apiLogin,
  logout as apiLogout,
  getMe,
  refreshToken as apiRefreshToken,
} from "@/lib/api";
import type { User, LoginRequest } from "@/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        setUser(await getMe());
      } catch {
        try {
          await apiRefreshToken();
          setUser(await getMe());
        } catch {
          clearTokens();
          setUser(null);
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchUser();
  }, []);

  const login = useCallback(async (credentials: LoginRequest) => {
    await apiLogin(credentials);
    setUser(await getMe());
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
