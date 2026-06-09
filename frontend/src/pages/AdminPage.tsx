import { FormEvent, useEffect, useState } from "react";
import { Ban, RotateCcw, Save } from "lucide-react";

import { api } from "../api/client";
import { AdminMatchBet, AdminTournamentBet, Match, Tournament, TournamentMarket } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { useToast } from "../context/ToastContext";

type ScoreDraft = {
  home_score: string;
  away_score: string;
};

type ScoreDrafts = Record<number, ScoreDraft>;
type TournamentMarketsById = Record<number, TournamentMarket[]>;
type WinnerDrafts = Record<number, string>;

export function AdminPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [tournamentMarkets, setTournamentMarkets] = useState<TournamentMarketsById>({});
  const [matchBets, setMatchBets] = useState<AdminMatchBet[]>([]);
  const [tournamentBets, setTournamentBets] = useState<AdminTournamentBet[]>([]);
  const [drafts, setDrafts] = useState<ScoreDrafts>({});
  const [winnerDrafts, setWinnerDrafts] = useState<WinnerDrafts>({});
  const [loading, setLoading] = useState(true);
  const [busyMatchId, setBusyMatchId] = useState<number | null>(null);
  const [busyTournamentId, setBusyTournamentId] = useState<number | null>(null);
  const [busyBetKey, setBusyBetKey] = useState<string | null>(null);
  const { showToast } = useToast();

  async function loadAdminData() {
    const response = await api.get<Match[]>("/matches");
    setMatches(response.data);
    setDrafts(
      Object.fromEntries(
        response.data.map((match) => [
          match.id,
          {
            home_score: match.home_score?.toString() ?? "",
            away_score: match.away_score?.toString() ?? ""
          }
        ])
      )
    );

    const tournamentResponse = await api.get<Tournament[]>("/tournaments");
    setTournaments(tournamentResponse.data);
    const marketEntries = await Promise.all(
      tournamentResponse.data.map(async (tournament) => {
        const marketResponse = await api.get<TournamentMarket[]>(`/tournaments/${tournament.id}/markets`);
        return [tournament.id, marketResponse.data] as const;
      })
    );
    const marketsByTournament = Object.fromEntries(marketEntries);
    setTournamentMarkets(marketsByTournament);
    setWinnerDrafts(
      Object.fromEntries(
        tournamentResponse.data.map((tournament) => [
          tournament.id,
          tournament.winner_team ?? marketsByTournament[tournament.id]?.[0]?.selection ?? ""
        ])
      )
    );

    const [matchBetsResponse, tournamentBetsResponse] = await Promise.all([
      api.get<AdminMatchBet[]>("/admin/bets/matches"),
      api.get<AdminTournamentBet[]>("/admin/bets/tournaments")
    ]);
    setMatchBets(matchBetsResponse.data);
    setTournamentBets(tournamentBetsResponse.data);
    setLoading(false);
  }

  useEffect(() => {
    void loadAdminData();
  }, []);

  function updateDraft(matchId: number, field: keyof ScoreDraft, value: string) {
    setDrafts((current) => ({
      ...current,
      [matchId]: {
        ...current[matchId],
        [field]: value
      }
    }));
  }

  async function setResult(event: FormEvent, matchId: number) {
    event.preventDefault();
    const draft = drafts[matchId];
    if (!draft) {
      return;
    }
    setBusyMatchId(matchId);
    try {
      await api.patch(`/admin/matches/${matchId}/result`, {
        home_score: Number(draft.home_score),
        away_score: Number(draft.away_score)
      });
      showToast("Match result settled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not set result");
    } finally {
      setBusyMatchId(null);
    }
  }

  async function unsettle(matchId: number) {
    setBusyMatchId(matchId);
    try {
      await api.post(`/admin/matches/${matchId}/unsettle`);
      showToast("Match unsettled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not unsettle match");
    } finally {
      setBusyMatchId(null);
    }
  }

  async function voidMatchBets(matchId: number) {
    setBusyMatchId(matchId);
    try {
      await api.post(`/admin/matches/${matchId}/void-bets`);
      showToast("Match bets voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not void match bets");
    } finally {
      setBusyMatchId(null);
    }
  }

  function updateWinnerDraft(tournamentId: number, value: string) {
    setWinnerDrafts((current) => ({
      ...current,
      [tournamentId]: value
    }));
  }

  async function settleTournament(event: FormEvent, tournamentId: number) {
    event.preventDefault();
    const winnerTeam = winnerDrafts[tournamentId];
    if (!winnerTeam) {
      return;
    }
    setBusyTournamentId(tournamentId);
    try {
      await api.patch(`/admin/tournaments/${tournamentId}/winner`, {
        winner_team: winnerTeam
      });
      showToast("Tournament settled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not settle tournament");
    } finally {
      setBusyTournamentId(null);
    }
  }

  async function unsettleTournament(tournamentId: number) {
    setBusyTournamentId(tournamentId);
    try {
      await api.patch(`/admin/tournaments/${tournamentId}/unsettle`);
      showToast("Tournament unsettled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not unsettle tournament");
    } finally {
      setBusyTournamentId(null);
    }
  }

  async function voidTournamentBets(tournamentId: number) {
    setBusyTournamentId(tournamentId);
    try {
      await api.patch(`/admin/tournaments/${tournamentId}/void-bets`);
      showToast("Tournament bets voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not void tournament bets");
    } finally {
      setBusyTournamentId(null);
    }
  }

  async function voidSingleMatchBet(betId: number) {
    const busyKey = `match-${betId}`;
    setBusyBetKey(busyKey);
    try {
      await api.post(`/admin/bets/matches/${betId}/void`);
      showToast("Match bet voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not void match bet");
    } finally {
      setBusyBetKey(null);
    }
  }

  async function voidSingleTournamentBet(betId: number) {
    const busyKey = `tournament-${betId}`;
    setBusyBetKey(busyKey);
    try {
      await api.post(`/admin/bets/tournaments/${betId}/void`);
      showToast("Tournament bet voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast("Could not void tournament bet");
    } finally {
      setBusyBetKey(null);
    }
  }

  return (
    <section className="space-y-4">
      <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
        <h1 className="text-lg font-bold text-ink">Admin Portal</h1>
        <p className="text-sm text-slate-500">Local testing controls for result settlement.</p>
      </div>

      {loading && <EmptyState title="Loading admin controls" />}
      {!loading &&
        <>
          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">Match Settlement</h2>
            </div>
            {matches.map((match) => {
              const draft = drafts[match.id] ?? { home_score: "", away_score: "" };
              const isBusy = busyMatchId === match.id;
              return (
                <article key={match.id} className="rounded-md border border-line bg-white p-4 shadow-sm">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <h2 className="text-base font-bold text-ink">
                        {match.home_team} vs {match.away_team}
                      </h2>
                      <p className="mt-1 text-sm text-slate-500">{new Date(match.kickoff_time).toLocaleString()}</p>
                    </div>
                    <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                      {match.status}
                    </span>
                  </div>

                  <form className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1fr_auto_auto_auto]" onSubmit={(event) => setResult(event, match.id)}>
                    <label className="block text-sm font-semibold text-slate-700">
                      {match.home_team}
                      <input
                        className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
                        min="0"
                        onChange={(event) => updateDraft(match.id, "home_score", event.target.value)}
                        type="number"
                        value={draft.home_score}
                      />
                    </label>
                    <label className="block text-sm font-semibold text-slate-700">
                      {match.away_team}
                      <input
                        className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
                        min="0"
                        onChange={(event) => updateDraft(match.id, "away_score", event.target.value)}
                        type="number"
                        value={draft.away_score}
                      />
                    </label>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md bg-ocean px-4 text-sm font-bold text-white hover:bg-blue-800 disabled:opacity-60"
                      disabled={isBusy || draft.home_score === "" || draft.away_score === ""}
                      type="submit"
                    >
                      <Save size={17} />
                      Set Result
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-line px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                      disabled={isBusy || match.status !== "COMPLETED"}
                      onClick={() => unsettle(match.id)}
                      type="button"
                    >
                      <RotateCcw size={17} />
                      Unsettle
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-red-200 px-4 text-sm font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
                      disabled={isBusy}
                      onClick={() => voidMatchBets(match.id)}
                      type="button"
                    >
                      <Ban size={17} />
                      Void Bets
                    </button>
                  </form>
                </article>
              );
            })}
          </section>

          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">Tournament Settlement</h2>
            </div>
            {tournaments.map((tournament) => {
              const markets = tournamentMarkets[tournament.id] ?? [];
              const isBusy = busyTournamentId === tournament.id;
              return (
                <article key={tournament.id} className="rounded-md border border-line bg-white p-4 shadow-sm">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <h2 className="text-base font-bold text-ink">{tournament.name}</h2>
                      <p className="mt-1 text-sm text-slate-500">
                        {tournament.year}
                        {tournament.winner_team ? ` · Winner: ${tournament.winner_team}` : ""}
                      </p>
                    </div>
                    <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                      {tournament.status}
                    </span>
                  </div>

                  <form className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-[minmax(0,1fr)_auto_auto_auto]" onSubmit={(event) => settleTournament(event, tournament.id)}>
                    <label className="block text-sm font-semibold text-slate-700">
                      Winner
                      <select
                        className="mt-1 h-11 w-full rounded-md border border-line bg-white px-3 outline-none focus:border-ocean"
                        onChange={(event) => updateWinnerDraft(tournament.id, event.target.value)}
                        value={winnerDrafts[tournament.id] ?? ""}
                      >
                        {markets.map((market) => (
                          <option key={market.id} value={market.selection}>
                            {market.selection}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md bg-ocean px-4 text-sm font-bold text-white hover:bg-blue-800 disabled:opacity-60"
                      disabled={isBusy || !winnerDrafts[tournament.id] || tournament.status === "COMPLETED"}
                      type="submit"
                    >
                      <Save size={17} />
                      Set Winner
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-line px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                      disabled={isBusy || tournament.status !== "COMPLETED"}
                      onClick={() => unsettleTournament(tournament.id)}
                      type="button"
                    >
                      <RotateCcw size={17} />
                      Unsettle
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-red-200 px-4 text-sm font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
                      disabled={isBusy}
                      onClick={() => voidTournamentBets(tournament.id)}
                      type="button"
                    >
                      <Ban size={17} />
                      Void Bets
                    </button>
                  </form>
                </article>
              );
            })}
          </section>

          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">Match Bets</h2>
              <p className="text-sm text-slate-500">Void one bet to refund its stake and reverse any winning payout.</p>
            </div>
            <div className="overflow-x-auto rounded-md border border-line bg-white shadow-sm">
              {matchBets.length === 0 ? (
                <div className="px-4 py-6 text-sm font-semibold text-slate-500">No match bets yet.</div>
              ) : (
                <table className="min-w-[980px] w-full text-left text-sm">
                  <thead className="border-b border-line bg-slate-50 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-4 py-3">User</th>
                      <th className="px-4 py-3">Match</th>
                      <th className="px-4 py-3">Market</th>
                      <th className="px-4 py-3">Selection</th>
                      <th className="px-4 py-3">Stake</th>
                      <th className="px-4 py-3">Payout</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {matchBets.map((bet) => {
                      const busyKey = `match-${bet.id}`;
                      return (
                        <tr key={bet.id}>
                          <td className="px-4 py-3 font-semibold text-ink">
                            {bet.username}
                            <span className="block text-xs font-medium text-slate-500">#{bet.user_id}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">
                            {bet.home_team} vs {bet.away_team}
                            <span className="block text-xs text-slate-500">{new Date(bet.kickoff_time).toLocaleString()}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">{bet.market_type}</td>
                          <td className="px-4 py-3 font-semibold text-ink">
                            {bet.selection}
                            <span className="block text-xs font-medium text-slate-500">@ {bet.odds}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">{bet.stake}</td>
                          <td className="px-4 py-3 text-slate-700">{bet.payout ?? "-"}</td>
                          <td className="px-4 py-3">
                            <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                              {bet.status}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <button
                              className="flex h-9 items-center justify-center gap-2 rounded-md border border-red-200 px-3 text-xs font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
                              disabled={busyBetKey === busyKey || bet.status === "VOID"}
                              onClick={() => voidSingleMatchBet(bet.id)}
                              type="button"
                            >
                              <Ban size={15} />
                              Void
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </section>

          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">Tournament Bets</h2>
              <p className="text-sm text-slate-500">Void one tournament bet to refund its stake and reverse any winner payout.</p>
            </div>
            <div className="overflow-x-auto rounded-md border border-line bg-white shadow-sm">
              {tournamentBets.length === 0 ? (
                <div className="px-4 py-6 text-sm font-semibold text-slate-500">No tournament bets yet.</div>
              ) : (
                <table className="min-w-[920px] w-full text-left text-sm">
                  <thead className="border-b border-line bg-slate-50 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-4 py-3">User</th>
                      <th className="px-4 py-3">Tournament</th>
                      <th className="px-4 py-3">Selection</th>
                      <th className="px-4 py-3">Stake</th>
                      <th className="px-4 py-3">Payout</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {tournamentBets.map((bet) => {
                      const busyKey = `tournament-${bet.id}`;
                      return (
                        <tr key={bet.id}>
                          <td className="px-4 py-3 font-semibold text-ink">
                            {bet.username}
                            <span className="block text-xs font-medium text-slate-500">#{bet.user_id}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">{bet.tournament_name}</td>
                          <td className="px-4 py-3 font-semibold text-ink">
                            {bet.selection}
                            <span className="block text-xs font-medium text-slate-500">@ {bet.odds}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">{bet.stake}</td>
                          <td className="px-4 py-3 text-slate-700">{bet.payout ?? "-"}</td>
                          <td className="px-4 py-3">
                            <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                              {bet.status}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <button
                              className="flex h-9 items-center justify-center gap-2 rounded-md border border-red-200 px-3 text-xs font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
                              disabled={busyBetKey === busyKey || bet.status === "VOID"}
                              onClick={() => voidSingleTournamentBet(bet.id)}
                              type="button"
                            >
                              <Ban size={15} />
                              Void
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        </>}
    </section>
  );
}
