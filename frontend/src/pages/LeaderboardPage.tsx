import { useEffect, useState } from "react";

import { api } from "../api/client";
import { LeaderboardEntry } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { useI18n } from "../context/I18nContext";

export function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useI18n();

  useEffect(() => {
    async function loadLeaderboard() {
      const response = await api.get<LeaderboardEntry[]>("/leaderboard");
      setEntries(response.data);
      setLoading(false);
    }

    void loadLeaderboard();
  }, []);

  return (
    <section className="rounded-md border border-line bg-white shadow-sm">
      <div className="border-b border-line px-4 py-3">
        <h1 className="text-lg font-bold text-ink">{t("leaderboard")}</h1>
      </div>
      {loading && <div className="p-4"><EmptyState title={t("loadingLeaderboard")} /></div>}
      {!loading && entries.length === 0 && <div className="p-4"><EmptyState title={t("noLeaderboardEntriesYet")} /></div>}
      {!loading && entries.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">{t("rank")}</th>
                <th className="px-4 py-3">{t("user")}</th>
                <th className="px-4 py-3 text-right">{t("balance")}</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.user_id} className="border-t border-line">
                  <td className="px-4 py-3 font-bold text-ink">{entry.rank}</td>
                  <td className="px-4 py-3 font-semibold text-slate-700">{entry.username}</td>
                  <td className="px-4 py-3 text-right font-bold text-emerald-700">{entry.balance.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
