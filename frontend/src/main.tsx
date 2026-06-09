import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { AdminRoute, ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import { AdminPage } from "./pages/AdminPage";
import { LeaderboardPage } from "./pages/LeaderboardPage";
import { LoginPage } from "./pages/LoginPage";
import { MatchesPage } from "./pages/MatchesPage";
import { MyBetsPage } from "./pages/MyBetsPage";
import { RegisterPage } from "./pages/RegisterPage";
import { TournamentDetailPage } from "./pages/TournamentDetailPage";
import { TournamentsPage } from "./pages/TournamentsPage";
import { WalletPage } from "./pages/WalletPage";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
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
              <Route path="/tournaments" element={<TournamentsPage />} />
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
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>
);
