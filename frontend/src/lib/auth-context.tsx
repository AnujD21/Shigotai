"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, ApiError, getToken, setToken } from "@/lib/api";
import type { User } from "@/lib/types";

interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  /** True when a token exists but we couldn't confirm the session (network
   * or server error) -- distinct from being genuinely logged out. Consumers
   * like AppShell should show a retry state instead of redirecting to
   * /login when this is true, so a backend hiccup doesn't look like the
   * user got signed out. */
  authError: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(false);

  const refreshUser = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setAuthError(false);
      setIsLoading(false);
      return;
    }
    try {
      const me = await api.get<User>("/auth/me");
      setUser(me);
      setAuthError(false);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setToken(null);
        setUser(null);
        setAuthError(false);
      } else {
        // Network failure or server error: we have a token but couldn't
        // verify it. Don't assume the user is logged out.
        setAuthError(true);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // One-time session check on mount, calling the shared refreshUser used
    // elsewhere for login/register too -- the sanctioned data-fetching
    // exception to this rule, not state derivable during render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await api.post<TokenResponse>("/auth/login", { email, password }, { auth: false });
      setToken(tokens.access_token);
      await refreshUser();
    },
    [refreshUser]
  );

  const register = useCallback(
    async (fullName: string, email: string, password: string) => {
      const tokens = await api.post<TokenResponse>(
        "/auth/register",
        { full_name: fullName, email, password },
        { auth: false }
      );
      setToken(tokens.access_token);
      await refreshUser();
    },
    [refreshUser]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    setAuthError(false);
  }, []);

  const value = useMemo(
    () => ({ user, isLoading, authError, login, register, logout, refreshUser }),
    [user, isLoading, authError, login, register, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
