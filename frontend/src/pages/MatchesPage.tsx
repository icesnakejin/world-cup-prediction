import { useEffect, useState } from "react";

import { api } from "../api/client";
import { Market, Match } from "../api/types";
import { BetSelection, BetSlip } from "../components/BetSlip";
import { EmptyState } from "../components/EmptyState";
import { MatchCard } from "../components/MatchCard";
import { useToast } from "../context/ToastContext";

type MarketMap = Record<number, Market[]>;

export function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [marketsByMatch, setMarketsByMatch] = useState<MarketMap>({});
  const [selected, setSelected] = useState<BetSelection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { showToast } = useToast();

  useEffect(() => {
    async function loadMatches() {
      setLoading(true);
      setError("");
      try {
        const matchResponse = await api.get<Match[]>("/matches");
        setMatches(matchResponse.data);
        const marketEntries = await Promise.all(
          matchResponse.data.map(async (match) => {
            const response = await api.get<Market[]>(`/matches/${match.id}/markets`);
            return [match.id, response.data] as const;
          })
        );
        setMarketsByMatch(Object.fromEntries(marketEntries));
      } catch {
        setError("Could not load matches.");
      } finally {
        setLoading(false);
      }
    }

    void loadMatches();
  }, []);

  async function placeBet(stake: number) {
    if (!selected) {
      return;
    }
    await api.post("/bets", { market_id: selected.market.id, stake });
    setSelected(null);
    window.dispatchEvent(new Event("wallet:refresh"));
    showToast("Bet placed successfully");
  }

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
      <section className="min-w-0 space-y-3">
        <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
          <h1 className="text-lg font-bold text-ink">World Cup Matches</h1>
          <p className="text-sm text-slate-500">Match winner markets use virtual coins only.</p>
        </div>
        {loading && <EmptyState title="Loading matches" />}
        {error && <EmptyState title={error} />}
        {!loading && !error && matches.length === 0 && <EmptyState title="No matches available" />}
        {!loading &&
          !error &&
          matches.map((match) => (
            <MatchCard
              key={match.id}
              match={match}
              markets={marketsByMatch[match.id] ?? []}
              onSelect={setSelected}
              selectedMarketId={selected?.market.id ?? null}
            />
          ))}
      </section>
      <aside className="hidden xl:block">
        <BetSlip onClear={() => setSelected(null)} onPlaceBet={placeBet} selection={selected} />
      </aside>
      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-[#eef3f8] p-3 shadow-2xl xl:hidden">
        <BetSlip onClear={() => setSelected(null)} onPlaceBet={placeBet} selection={selected} />
      </div>
    </div>
  );
}
