import { Trophy, Wallet } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import { Wallet as WalletType } from "../api/types";
import { isAdminEmail } from "../config/admin";
import { useAuth } from "../context/AuthContext";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    "px-3 py-2 text-sm font-semibold transition",
    isActive ? "border-b-2 border-white text-white" : "text-blue-100 hover:text-white"
  ].join(" ");

export function AppLayout() {
  const { logout, user } = useAuth();
  const [balance, setBalance] = useState<number | null>(null);
  const isAdmin = isAdminEmail(user?.email);

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
              <p className="text-base font-bold sm:text-lg">World Cup Prediction League</p>
              <p className="text-xs text-blue-100">{user?.username}</p>
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-1">
            <NavLink className={navLinkClass} to="/matches">
              Matches
            </NavLink>
            <NavLink className={navLinkClass} to="/tournaments">
              Tournaments
            </NavLink>
            <NavLink className={navLinkClass} to="/my-bets">
              My Bets
            </NavLink>
            <NavLink className={navLinkClass} to="/leaderboard">
              Leaderboard
            </NavLink>
            <NavLink className={navLinkClass} to="/wallet">
              Wallet
            </NavLink>
            {isAdmin && (
              <NavLink className={navLinkClass} to="/admin">
                Admin
              </NavLink>
            )}
          </nav>
          <div className="flex items-center justify-between gap-3 lg:justify-end">
            <div className="flex h-10 items-center gap-2 rounded-md bg-blue-950/35 px-3 text-sm font-semibold">
              <Wallet size={17} />
              {balance === null ? "-" : balance.toLocaleString()} coins
            </div>
            <button
              className="h-10 rounded-md border border-blue-200 px-3 text-sm font-semibold text-white hover:bg-white hover:text-ocean"
              onClick={logout}
              type="button"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1440px] grid-cols-1 gap-4 px-4 py-4 lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="hidden rounded-md border border-line bg-white p-3 lg:block">
          <p className="mb-3 text-xs font-bold uppercase tracking-wide text-slate-500">Tournament</p>
          <nav className="space-y-1">
            {["World Cup", "Group Stage", "Knockout Stage"].map((item) => (
              <button
                key={item}
                className="flex w-full items-center rounded-md px-3 py-2 text-left text-sm font-semibold text-slate-700 hover:bg-blue-50 hover:text-ocean"
                type="button"
              >
                {item}
              </button>
            ))}
          </nav>
        </aside>
        <main className="min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
