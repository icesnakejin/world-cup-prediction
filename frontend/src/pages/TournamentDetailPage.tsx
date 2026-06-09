import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Send } from "lucide-react";

import { api } from "../api/client";
import { Tournament, TournamentBet, TournamentMarket } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { useToast } from "../context/ToastContext";

export function TournamentDetailPage() {
  const { id } = useParams();
  const tournamentId = Number(id);
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [markets, setMarkets] = useState<TournamentMarket[]>([]);
  const [bets, setBets] = useState<TournamentBet[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<TournamentMarket | null>(null);
  const [stake, setStake] = useState("100");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const { showToast } = useToast();

  const stakeNumber = Number(stake || 0);
  const potentialPayout = useMemo(
    () => (selectedMarket && stakeNumber > 0 ? stakeNumber * Number(selectedMarket.odds) : 0),
    [selectedMarket, stakeNumber]
  );

  async function loadTournamentData() {
    const [tournamentResponse, marketResponse, betsResponse] = await Promise.all([
      api.get<Tournament>(`/tournaments/${tournamentId}`),
      api.get<TournamentMarket[]>(`/tournaments/${tournamentId}/markets`),
      api.get<TournamentBet[]>("/tournament-bets/me")
    ]);
    setTournament(tournamentResponse.data);
    setMarkets(marketResponse.data);
    setBets(betsResponse.data.filter((bet) => bet.tournament_id === tournamentId));
    setLoading(false);
  }

  useEffect(() => {
    void loadTournamentData();
  }, [tournamentId]);

  async function placeBet(event: FormEvent) {
    event.preventDefault();
    if (!selectedMarket || stakeNumber <= 0) {
      return;
    }

    setSubmitting(true);
    try {
      await api.post("/tournament-bets", {
        tournament_market_id: selectedMarket.id,
        stake: stakeNumber
      });
      setSelectedMarket(null);
      setStake("100");
      await loadTournamentData();
      window.dispatchEvent(new Event("wallet:refresh"));
      showToast("Tournament bet placed");
    } catch {
      showToast("Could not place tournament bet");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <EmptyState title="Loading tournament" />;
  }

  if (!tournament) {
    return <EmptyState title="Tournament not found" />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
      <section className="space-y-3">
        <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h1 className="text-lg font-bold text-ink">{tournament.name}</h1>
              <p className="text-sm text-slate-500">{tournament.year}</p>
            </div>
            <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
              {tournament.status}
            </span>
          </div>
        </div>

        <section className="rounded-md border border-line bg-white shadow-sm">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-bold uppercase tracking-wide text-slate-600">Tournament Winner</h2>
          </div>
          <div className="max-h-[65vh] grid gap-2 overflow-y-auto p-3 pr-2 sm:grid-cols-2 lg:grid-cols-3">
            {markets.map((market) => (
              <button
                className={[
                  "rounded-md border px-3 py-3 text-left transition",
                  selectedMarket?.id === market.id
                    ? "border-emerald-700 bg-emerald-50 text-emerald-800"
                    : "border-blue-300 bg-white text-ocean hover:bg-blue-50"
                ].join(" ")}
                key={market.id}
                onClick={() => setSelectedMarket(market)}
                type="button"
              >
                <span className="block text-sm font-bold text-ink">{market.selection}</span>
                <span className="mt-1 block text-lg font-bold">{market.odds}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-md border border-line bg-white shadow-sm">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-bold uppercase tracking-wide text-slate-600">My Tournament Bets</h2>
          </div>
          {bets.length === 0 ? (
            <div className="p-4">
              <EmptyState title="No tournament bets yet" />
            </div>
          ) : (
            <div className="divide-y divide-line">
              {bets.map((bet) => (
                <div className="grid gap-2 px-4 py-3 text-sm sm:grid-cols-5" key={bet.id}>
                  <p className="font-bold text-ink">{bet.selection}</p>
                  <p>Stake: {bet.stake}</p>
                  <p>Odds: {bet.odds}</p>
                  <p>Payout: {bet.payout ?? Math.round(bet.stake * Number(bet.odds))}</p>
                  <p className="font-bold text-slate-600">{bet.status}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </section>

      <aside className="rounded-md border border-line bg-white shadow-sm xl:sticky xl:top-24 xl:h-fit">
        <div className="border-b border-line px-4 py-3">
          <h2 className="text-sm font-bold uppercase tracking-wide text-slate-600">Tournament Bet Slip</h2>
        </div>
        <form className="space-y-4 p-4" onSubmit={placeBet}>
          {selectedMarket ? (
            <div>
              <p className="font-bold text-ink">{selectedMarket.selection}</p>
              <p className="mt-1 text-sm text-slate-500">Odds {selectedMarket.odds}</p>
            </div>
          ) : (
            <p className="text-sm font-semibold text-slate-500">Select a team to place a tournament winner bet.</p>
          )}
          <label className="block text-sm font-semibold text-slate-700">
            Stake
            <input
              className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
              min="1"
              onChange={(event) => setStake(event.target.value)}
              type="number"
              value={stake}
            />
          </label>
          <div className="rounded-md bg-slate-50 p-3">
            <p className="text-xs font-bold uppercase text-slate-500">Potential payout</p>
            <p className="mt-1 text-lg font-bold text-emerald-700">{potentialPayout.toFixed(0)}</p>
          </div>
          <button
            className="flex h-11 w-full items-center justify-center gap-2 rounded-md bg-emerald-700 text-sm font-bold text-white hover:bg-emerald-800 disabled:opacity-60"
            disabled={!selectedMarket || submitting || stakeNumber <= 0}
            type="submit"
          >
            <Send size={17} />
            {submitting ? "Placing bet" : "Place Bet"}
          </button>
        </form>
      </aside>
    </div>
  );
}
