import { useEffect, useState } from "react";

import { api } from "../api/client";
import { Bet } from "../api/types";
import { EmptyState } from "../components/EmptyState";

export function MyBetsPage() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadBets() {
      const response = await api.get<Bet[]>("/bets/me");
      setBets(response.data);
      setLoading(false);
    }

    void loadBets();
  }, []);

  return (
    <section className="space-y-3">
      <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
        <h1 className="text-lg font-bold text-ink">My Bets</h1>
      </div>
      {loading && <EmptyState title="Loading bets" />}
      {!loading && bets.length === 0 && <EmptyState title="No bets placed yet" />}
      <div className="space-y-3">
        {bets.map((bet) => (
          <article key={bet.bet_id} className="rounded-md border border-line bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-base font-bold text-ink">
                  {bet.match.home_team} vs {bet.match.away_team}
                </h2>
                <p className="mt-1 text-sm text-slate-500">{new Date(bet.match.kickoff_time).toLocaleString()}</p>
                <p className="mt-2 text-sm font-bold text-ocean">{bet.selection}</p>
              </div>
              <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                {bet.status}
              </span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
              <Metric label="Stake" value={bet.stake.toLocaleString()} />
              <Metric label="Odds" value={bet.odds} />
              <Metric label="Payout" value={bet.payout === null ? "-" : bet.payout.toLocaleString()} />
              <Metric label="Placed" value={new Date(bet.created_at).toLocaleDateString()} />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <p className="text-xs font-bold uppercase text-slate-500">{label}</p>
      <p className="mt-1 font-bold text-ink">{value}</p>
    </div>
  );
}
