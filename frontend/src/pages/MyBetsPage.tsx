import { useEffect, useState } from "react";

import { api } from "../api/client";
import { Bet } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { useI18n } from "../context/I18nContext";
import { formatDate, formatDateTime, getMatchStatusLabel, getSelectionLabel } from "../i18n";

export function MyBetsPage() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [loading, setLoading] = useState(true);
  const { locale, t } = useI18n();

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
        <h1 className="text-lg font-bold text-ink">{t("myBets")}</h1>
      </div>
      {loading && <EmptyState title={t("loadingBets")} />}
      {!loading && bets.length === 0 && <EmptyState title={t("noBetsPlacedYet")} />}
      <div className="space-y-3">
        {bets.map((bet) => (
          <article key={bet.bet_id} className="rounded-md border border-line bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-base font-bold text-ink">
                  {bet.match.home_team ?? bet.match.home_placeholder ?? (locale === "zh" ? "待定" : "TBD")} vs{" "}
                  {bet.match.away_team ?? bet.match.away_placeholder ?? (locale === "zh" ? "待定" : "TBD")}
                </h2>
                <p className="mt-1 text-sm text-slate-500">{formatDateTime(bet.match.kickoff_time, locale)}</p>
                <p className="mt-2 text-sm font-bold text-ocean">{getSelectionLabel(bet.selection, locale)}</p>
              </div>
              <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                {getMatchStatusLabel(bet.status, locale)}
              </span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
              <Metric label={t("stake")} value={bet.stake.toLocaleString()} />
              <Metric label={t("odds")} value={bet.odds} />
              <Metric label={t("potentialPayout")} value={bet.payout === null ? "-" : bet.payout.toLocaleString()} />
              <Metric label={t("placed")} value={formatDate(bet.created_at, locale)} />
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
