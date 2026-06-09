import { useEffect, useState } from "react";

import { api } from "../api/client";
import { LeaderboardEntry } from "../api/types";
import { EmptyState } from "../components/EmptyState";

export function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

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
        <h1 className="text-lg font-bold text-ink">Leaderboard</h1>
      </div>
      {loading && <div className="p-4"><EmptyState title="Loading leaderboard" /></div>}
      {!loading && entries.length === 0 && <div className="p-4"><EmptyState title="No leaderboard entries yet" /></div>}
      {!loading && entries.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="bg-slate-50 text-xs font-bold uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3 text-right">Balance</th>
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
