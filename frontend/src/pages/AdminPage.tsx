import { FormEvent, useEffect, useState } from "react";
import { Ban, Database, RotateCcw, Save } from "lucide-react";

import { api } from "../api/client";
import { AdminMatchBet, AdminTournamentBet, Match, Tournament, TournamentMarket } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../context/ToastContext";
import { getAwayName, getHomeName, getMatchTitle } from "../utils/matchDisplay";
import { formatDateTime, getMatchStatusLabel, getMarketGroupTitle, getSelectionLabel, getTournamentStatusLabel } from "../i18n";

type ScoreDraft = {
  home_score: string;
  away_score: string;
};

type ScoreDrafts = Record<number, ScoreDraft>;
type TournamentMarketsById = Record<number, TournamentMarket[]>;
type WinnerDrafts = Record<number, string>;

export function AdminPage() {
  const { locale, t } = useI18n();
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
  const [seeding, setSeeding] = useState(false);
  const [seedingGroupStage, setSeedingGroupStage] = useState(false);
  const [seedingTournamentMarkets, setSeedingTournamentMarkets] = useState(false);
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
      showToast(locale === "zh" ? "比赛结果已结算" : "Match result settled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法设置比赛结果" : "Could not set result");
    } finally {
      setBusyMatchId(null);
    }
  }

  async function unsettle(matchId: number) {
    setBusyMatchId(matchId);
    try {
      await api.post(`/admin/matches/${matchId}/unsettle`);
      showToast(locale === "zh" ? "比赛已撤销结算" : "Match unsettled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法撤销比赛结算" : "Could not unsettle match");
    } finally {
      setBusyMatchId(null);
    }
  }

  async function voidMatchBets(matchId: number) {
    setBusyMatchId(matchId);
    try {
      await api.post(`/admin/matches/${matchId}/void-bets`);
      showToast(locale === "zh" ? "比赛下注已作废" : "Match bets voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法作废比赛下注" : "Could not void match bets");
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
      showToast(locale === "zh" ? "冠军已结算" : "Tournament settled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法结算冠军市场" : "Could not settle tournament");
    } finally {
      setBusyTournamentId(null);
    }
  }

  async function unsettleTournament(tournamentId: number) {
    setBusyTournamentId(tournamentId);
    try {
      await api.patch(`/admin/tournaments/${tournamentId}/unsettle`);
      showToast(locale === "zh" ? "冠军已撤销结算" : "Tournament unsettled");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法撤销冠军结算" : "Could not unsettle tournament");
    } finally {
      setBusyTournamentId(null);
    }
  }

  async function voidTournamentBets(tournamentId: number) {
    setBusyTournamentId(tournamentId);
    try {
      await api.patch(`/admin/tournaments/${tournamentId}/void-bets`);
      showToast(locale === "zh" ? "冠军下注已作废" : "Tournament bets voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法作废冠军下注" : "Could not void tournament bets");
    } finally {
      setBusyTournamentId(null);
    }
  }

  async function voidSingleMatchBet(betId: number) {
    const busyKey = `match-${betId}`;
    setBusyBetKey(busyKey);
    try {
      await api.post(`/admin/bets/matches/${betId}/void`);
      showToast(locale === "zh" ? "比赛下注已作废" : "Match bet voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法作废比赛下注" : "Could not void match bet");
    } finally {
      setBusyBetKey(null);
    }
  }

  async function voidSingleTournamentBet(betId: number) {
    const busyKey = `tournament-${betId}`;
    setBusyBetKey(busyKey);
    try {
      await api.post(`/admin/bets/tournaments/${betId}/void`);
      showToast(locale === "zh" ? "冠军下注已作废" : "Tournament bet voided");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法作废冠军下注" : "Could not void tournament bet");
    } finally {
      setBusyBetKey(null);
    }
  }

  async function seedInitialData() {
    setSeeding(true);
    try {
      await api.post("/admin/seed/initial-data");
      showToast(locale === "zh" ? "示例数据已导入" : "Sample data imported");
      await loadAdminData();
      window.dispatchEvent(new Event("wallet:refresh"));
    } catch {
      showToast(locale === "zh" ? "无法导入示例数据" : "Could not import sample data");
    } finally {
      setSeeding(false);
    }
  }

  async function seedGroupStage() {
    setSeedingGroupStage(true);
    try {
      await api.post("/admin/seed/group-stage");
      showToast(locale === "zh" ? "2026 世界杯比赛和钱包已重置" : "World Cup 2026 matches and wallets reset");
      await loadAdminData();
    } catch {
      showToast(locale === "zh" ? "无法重置 2026 世界杯数据" : "Could not reset World Cup 2026 data");
    } finally {
      setSeedingGroupStage(false);
    }
  }

  async function seedTournamentMarkets() {
    setSeedingTournamentMarkets(true);
    try {
      await api.post("/admin/seed/tournament-markets");
      showToast(locale === "zh" ? "冠军市场已生成" : "Tournament winner markets seeded");
      await loadAdminData();
    } catch {
      showToast(locale === "zh" ? "无法生成冠军市场" : "Could not seed tournament markets");
    } finally {
      setSeedingTournamentMarkets(false);
    }
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 rounded-md border border-line bg-white px-4 py-3 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-lg font-bold text-ink">{t("adminPortal")}</h1>
          <p className="text-sm text-slate-500">{t("deploymentAndLocalTestingControls")}</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <button
            className="flex h-10 items-center justify-center gap-2 rounded-md border border-line px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
            disabled={seeding}
            onClick={seedInitialData}
            type="button"
          >
            <Database size={17} />
            {t("importSampleData")}
          </button>
          <button
            className="flex h-10 items-center justify-center gap-2 rounded-md bg-ocean px-4 text-sm font-bold text-white hover:bg-blue-800 disabled:opacity-60"
            disabled={seedingGroupStage}
            onClick={seedGroupStage}
            type="button"
          >
            <Database size={17} />
            {t("resetToWorldCup2026")}
          </button>
          <button
            className="flex h-10 items-center justify-center gap-2 rounded-md border border-line px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
            disabled={seedingTournamentMarkets}
            onClick={seedTournamentMarkets}
            type="button"
          >
            <Database size={17} />
            {t("seedTournamentMarkets")}
          </button>
        </div>
      </div>

      {loading && <EmptyState title={t("loadingAdminControls")} />}
      {!loading &&
        <>
          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">{t("matchSettlement")}</h2>
            </div>
            {matches.map((match) => {
              const draft = drafts[match.id] ?? { home_score: "", away_score: "" };
              const isBusy = busyMatchId === match.id;
              return (
                <article key={match.id} className="rounded-md border border-line bg-white p-4 shadow-sm">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <h2 className="text-base font-bold text-ink">
                        {getMatchTitle(match, locale)}
                      </h2>
                      <p className="mt-1 text-sm text-slate-500">{formatDateTime(match.kickoff_time, locale)}</p>
                    </div>
                    <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                      {getMatchStatusLabel(match.status, locale)}
                    </span>
                  </div>

                  <form className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1fr_auto_auto_auto]" onSubmit={(event) => setResult(event, match.id)}>
                    <label className="block text-sm font-semibold text-slate-700">
                      {getHomeName(match, locale)}
                      <input
                        className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
                        min="0"
                        onChange={(event) => updateDraft(match.id, "home_score", event.target.value)}
                        type="number"
                        value={draft.home_score}
                      />
                    </label>
                    <label className="block text-sm font-semibold text-slate-700">
                      {getAwayName(match, locale)}
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
                      {t("setResult")}
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-line px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                      disabled={isBusy || match.status !== "COMPLETED"}
                      onClick={() => unsettle(match.id)}
                      type="button"
                    >
                      <RotateCcw size={17} />
                      {t("unsettle")}
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-red-200 px-4 text-sm font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
                      disabled={isBusy}
                      onClick={() => voidMatchBets(match.id)}
                      type="button"
                    >
                      <Ban size={17} />
                      {t("voidBets")}
                    </button>
                  </form>
                </article>
              );
            })}
          </section>

          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">{t("tournamentSettlement")}</h2>
            </div>
            {tournaments.map((tournament) => {
              const markets = tournamentMarkets[tournament.id] ?? [];
              const isBusy = busyTournamentId === tournament.id;
              return (
                <article key={tournament.id} className="rounded-md border border-line bg-white p-4 shadow-sm">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <h2 className="text-base font-bold text-ink">{t("worldChampion")}</h2>
                      <p className="mt-1 text-sm text-slate-500">
                        {tournament.year}
                        {tournament.winner_team ? ` · ${t("winner")}: ${tournament.winner_team}` : ""}
                      </p>
                    </div>
                    <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                      {getTournamentStatusLabel(tournament.status, locale)}
                    </span>
                  </div>

                  <form className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-[minmax(0,1fr)_auto_auto_auto]" onSubmit={(event) => settleTournament(event, tournament.id)}>
                    <label className="block text-sm font-semibold text-slate-700">
                      {locale === "zh" ? "冠军" : "Winner"}
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
                      {t("setWinner")}
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-line px-4 text-sm font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                      disabled={isBusy || tournament.status !== "COMPLETED"}
                      onClick={() => unsettleTournament(tournament.id)}
                      type="button"
                    >
                      <RotateCcw size={17} />
                      {t("unsettle")}
                    </button>
                    <button
                      className="mt-auto flex h-11 items-center justify-center gap-2 rounded-md border border-red-200 px-4 text-sm font-bold text-red-700 hover:bg-red-50 disabled:opacity-60"
                      disabled={isBusy}
                      onClick={() => voidTournamentBets(tournament.id)}
                      type="button"
                    >
                      <Ban size={17} />
                      {t("voidBets")}
                    </button>
                  </form>
                </article>
              );
            })}
          </section>

          <section className="space-y-3">
            <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
              <h2 className="text-base font-bold text-ink">{t("matchBets")}</h2>
              <p className="text-sm text-slate-500">
                {locale === "zh"
                  ? "作废单笔下注会退回本金，并撤销可能的中奖返还。"
                  : "Void one bet to refund its stake and reverse any winning payout."}
              </p>
            </div>
            <div className="overflow-x-auto rounded-md border border-line bg-white shadow-sm">
              {matchBets.length === 0 ? (
                <div className="px-4 py-6 text-sm font-semibold text-slate-500">
                  {locale === "zh" ? "暂无比赛下注。" : "No match bets yet."}
                </div>
              ) : (
                <table className="min-w-[980px] w-full text-left text-sm">
                  <thead className="border-b border-line bg-slate-50 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-4 py-3">{t("user")}</th>
                      <th className="px-4 py-3">{t("matches")}</th>
                      <th className="px-4 py-3">{t("market")}</th>
                      <th className="px-4 py-3">{t("selection")}</th>
                      <th className="px-4 py-3">{t("stake")}</th>
                      <th className="px-4 py-3">{t("potentialPayout")}</th>
                      <th className="px-4 py-3">{t("status")}</th>
                      <th className="px-4 py-3">{t("action")}</th>
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
                            {getHomeName(
                              {
                                home_team: bet.home_team,
                                away_team: bet.away_team,
                                home_placeholder: bet.home_placeholder,
                                away_placeholder: bet.away_placeholder
                              } as Match,
                              locale
                            )}{" "}
                            vs{" "}
                            {getAwayName(
                              {
                                home_team: bet.home_team,
                                away_team: bet.away_team,
                                home_placeholder: bet.home_placeholder,
                                away_placeholder: bet.away_placeholder
                              } as Match,
                              locale
                            )}
                            <span className="block text-xs text-slate-500">{formatDateTime(bet.kickoff_time, locale)}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">
                            {getMarketGroupTitle(
                              { market_type: bet.market_type, selection: bet.selection, line: null } as never,
                              locale
                            )}
                          </td>
                          <td className="px-4 py-3 font-semibold text-ink">
                            {getSelectionLabel(bet.selection, locale)}
                            <span className="block text-xs font-medium text-slate-500">@ {bet.odds}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-700">{bet.stake}</td>
                          <td className="px-4 py-3 text-slate-700">{bet.payout ?? "-"}</td>
                          <td className="px-4 py-3">
                            <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                              {getMatchStatusLabel(bet.status, locale)}
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
                              {t("void")}
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
              <h2 className="text-base font-bold text-ink">{t("tournamentBets")}</h2>
              <p className="text-sm text-slate-500">
                {locale === "zh"
                  ? "作废单笔冠军下注会退回本金，并撤销中奖返还。"
                  : "Void one tournament bet to refund its stake and reverse any winner payout."}
              </p>
            </div>
            <div className="overflow-x-auto rounded-md border border-line bg-white shadow-sm">
              {tournamentBets.length === 0 ? (
                <div className="px-4 py-6 text-sm font-semibold text-slate-500">
                  {locale === "zh" ? "暂无冠军下注。" : "No tournament bets yet."}
                </div>
              ) : (
                <table className="min-w-[920px] w-full text-left text-sm">
                  <thead className="border-b border-line bg-slate-50 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-4 py-3">{t("user")}</th>
                      <th className="px-4 py-3">{t("worldChampion")}</th>
                      <th className="px-4 py-3">{t("selection")}</th>
                      <th className="px-4 py-3">{t("stake")}</th>
                      <th className="px-4 py-3">{t("potentialPayout")}</th>
                      <th className="px-4 py-3">{t("status")}</th>
                      <th className="px-4 py-3">{t("action")}</th>
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
                              {getMatchStatusLabel(bet.status, locale)}
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
                              {t("void")}
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
