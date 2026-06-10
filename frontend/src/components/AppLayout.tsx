import { Trophy, Wallet } from "lucide-react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import { Wallet as WalletType } from "../api/types";
import { isAdminEmail } from "../config/admin";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useAuth } from "../context/AuthContext";
import { useI18n } from "../context/I18nContext";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "px-3 py-2 text-sm font-semibold transition",
    isActive ? "border-b-2 border-white text-white" : "text-blue-100 hover:text-white"
  ].join(" ");

export function AppLayout() {
  const { logout, user } = useAuth();
  const { t } = useI18n();
  const [balance, setBalance] = useState<number | null>(null);
  const isAdmin = isAdminEmail(user?.email);
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const currentStage = searchParams.get("stage") ?? "group";
  const showTournamentSidebar = location.pathname === "/matches";

  useEffect(() => {
    async function loadBalance() {
      try {
        const response = await api.get<WalletType>("/wallet");
        setBalance(response.data.balance);
      } catch {
        setBalance(null);
      }
    }

    void loadBalance();
    window.addEventListener("wallet:refresh", loadBalance);
    return () => window.removeEventListener("wallet:refresh", loadBalance);
  }, []);

  return (
    <div className="min-h-screen bg-[#eef3f8]">
      <header className="sticky top-0 z-40 border-b border-blue-900 bg-ocean text-white shadow-sm">
        <div className="mx-auto flex max-w-[1440px] flex-col gap-3 px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-white text-ocean">
              <Trophy size={22} />
            </div>
            <div>
              <p className="text-base font-bold sm:text-lg">{t("appName")}</p>
              <p className="text-xs text-blue-100">{user?.username}</p>
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-1">
            <NavLink className={navLinkClass} to="/matches?stage=group">
              {t("matches")}
            </NavLink>
            <NavLink className={navLinkClass} to="/tournaments/1">
              {t("worldChampion")}
            </NavLink>
            <NavLink className={navLinkClass} to="/my-bets">
              {t("myBets")}
            </NavLink>
            <NavLink className={navLinkClass} to="/leaderboard">
              {t("leaderboard")}
            </NavLink>
            <NavLink className={navLinkClass} to="/wallet">
              {t("wallet")}
            </NavLink>
            {isAdmin && (
              <NavLink className={navLinkClass} to="/admin">
                {t("admin")}
              </NavLink>
            )}
          </nav>
          <div className="flex flex-wrap items-center justify-between gap-3 lg:justify-end">
            <LanguageSwitcher />
            <div className="flex h-10 items-center gap-2 rounded-md bg-blue-950/35 px-3 text-sm font-semibold">
              <Wallet size={17} />
              {balance === null ? "-" : balance.toLocaleString()} {t("coins")}
            </div>
            <button
              className="h-10 rounded-md border border-blue-200 px-3 text-sm font-semibold text-white hover:bg-white hover:text-ocean"
              onClick={logout}
              type="button"
            >
              {t("logout")}
            </button>
          </div>
        </div>
      </header>

      <div
        className={[
          "mx-auto grid max-w-[1440px] grid-cols-1 gap-4 px-4 py-4",
          showTournamentSidebar ? "lg:grid-cols-[220px_minmax(0,1fr)]" : "lg:grid-cols-1"
        ].join(" ")}
      >
        {showTournamentSidebar && (
          <aside className="hidden rounded-md border border-line bg-white p-3 lg:block">
            <p className="mb-3 text-xs font-bold uppercase tracking-wide text-slate-500">{t("tournaments")}</p>
            <nav className="space-y-1">
              <Link
                className={[
                  "flex w-full items-center rounded-md px-3 py-2 text-left text-sm font-semibold transition",
                  currentStage === "group" ? "bg-blue-50 text-ocean" : "text-slate-700 hover:bg-blue-50 hover:text-ocean"
                ].join(" ")}
                to="/matches?stage=group"
              >
                {t("groupStage")}
              </Link>
              <Link
                className={[
                  "flex w-full items-center rounded-md px-3 py-2 text-left text-sm font-semibold transition",
                  currentStage === "knockout" ? "bg-blue-50 text-ocean" : "text-slate-700 hover:bg-blue-50 hover:text-ocean"
                ].join(" ")}
                to="/matches?stage=knockout"
              >
                {t("knockoutStage")}
              </Link>
            </nav>
          </aside>
        )}
        <main className="min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
