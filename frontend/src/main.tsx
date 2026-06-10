import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { AdminRoute, ProtectedRoute } from "./components/ProtectedRoute";
import { I18nProvider } from "./context/I18nContext";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import { AdminPage } from "./pages/AdminPage";
import { LeaderboardPage } from "./pages/LeaderboardPage";
import { LoginPage } from "./pages/LoginPage";
import { MatchesPage } from "./pages/MatchesPage";
import { MyBetsPage } from "./pages/MyBetsPage";
import { RegisterPage } from "./pages/RegisterPage";
import { TournamentDetailPage } from "./pages/TournamentDetailPage";
import { WalletPage } from "./pages/WalletPage";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <I18nProvider>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route path="/matches" element={<MatchesPage />} />
                <Route path="/tournaments" element={<Navigate to="/tournaments/1" replace />} />
                <Route path="/tournaments/:id" element={<TournamentDetailPage />} />
                <Route path="/my-bets" element={<MyBetsPage />} />
                <Route path="/wallet" element={<WalletPage />} />
                <Route path="/leaderboard" element={<LeaderboardPage />} />
                <Route
                  path="/admin"
                  element={
                    <AdminRoute>
                      <AdminPage />
                    </AdminRoute>
                  }
                />
              </Route>
              <Route path="*" element={<Navigate to="/matches" replace />} />
            </Routes>
          </AuthProvider>
        </I18nProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>
);
