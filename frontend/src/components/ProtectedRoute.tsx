import { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { isAdminEmail } from "../config/admin";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { token, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 text-sm font-semibold text-slate-600">
        Loading
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export function AdminRoute({ children }: { children: ReactNode }) {
  const { loading, user } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 text-sm font-semibold text-slate-600">
        Loading
      </div>
    );
  }

  if (!isAdminEmail(user?.email)) {
    return <Navigate to="/matches" replace />;
  }

  return <>{children}</>;
}
