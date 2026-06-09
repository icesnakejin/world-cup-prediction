import { createContext, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";
import { TokenResponse, User } from "../api/types";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("wcp_token"));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function refreshUser() {
    const response = await api.get<User>("/me");
    setUser(response.data);
  }

  async function login(email: string, password: string) {
    const response = await api.post<TokenResponse>("/auth/login", { email, password });
    localStorage.setItem("wcp_token", response.data.access_token);
    setToken(response.data.access_token);
    await refreshUser();
    navigate("/matches");
  }

  async function register(username: string, email: string, password: string) {
    await api.post<User>("/auth/register", { username, email, password });
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem("wcp_token");
    setToken(null);
    setUser(null);
    navigate("/login");
  }

  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        await refreshUser();
      } catch {
        localStorage.removeItem("wcp_token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    void loadUser();
  }, [token]);

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout, refreshUser }),
    [user, token, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
