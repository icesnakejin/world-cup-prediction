import { Clock } from "lucide-react";

import { Match, Market } from "../api/types";
import { useI18n } from "../context/I18nContext";
import { formatDateTime, getMatchStatusLabel, getMatchTitle, getSelectionLabel } from "../i18n";
import { BetSelection } from "./BetSlip";

type MatchCardProps = {
  match: Match;
  markets: Market[];
  selectedMarketId: number | null;
  onSelect: (selection: BetSelection) => void;
};

export function MatchCard({ match, markets, selectedMarketId, onSelect }: MatchCardProps) {
  const { locale } = useI18n();
  const bettingDisabled = match.stage !== "group";
  const teamWinMarkets = markets.filter((market) => market.market_type === "match_winner");
  const overUnderMarkets = markets.filter((market) => market.market_type === "over_under");
  const exactScoreMarkets = markets.filter((market) => market.market_type === "exact_score");

  return (
    <article className="rounded-md border border-line bg-white shadow-sm">
      <div className="border-b border-line px-4 py-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-base font-bold text-ink">
              {getMatchTitle(match, locale)}
            </h2>
            <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-semibold text-slate-500">
              {match.match_number && <span>{locale === "zh" ? "第" : "Match "}{match.match_number}{locale === "zh" ? " 场" : ""}</span>}
              <span className="flex items-center gap-1">
                <Clock size={14} />
                {formatDateTime(match.kickoff_time, locale)}
              </span>
              {match.venue && <span>{match.venue}</span>}
            </div>
          </div>
          <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
            {getMatchStatusLabel(match.status, locale)}
          </span>
        </div>
      </div>
      <div className="space-y-4 p-3">
        <MarketGroup
          gridClassName="grid-cols-3"
          markets={teamWinMarkets}
          match={match}
          onSelect={onSelect}
          selectedMarketId={selectedMarketId}
          disabled={bettingDisabled}
          locale={locale}
          title={locale === "zh" ? "胜平负" : "Team Win"}
        />
        <MarketGroup
          gridClassName="grid-cols-2"
          markets={overUnderMarkets}
          match={match}
          onSelect={onSelect}
          selectedMarketId={selectedMarketId}
          disabled={bettingDisabled}
          locale={locale}
          title={overUnderMarkets[0]?.line ? `${locale === "zh" ? "大小球" : "Over/Under"} ${Number(overUnderMarkets[0].line).toFixed(1)}` : locale === "zh" ? "大小球" : "Over/Under"}
        />
        <MarketGroup
          gridClassName="grid-cols-2 sm:grid-cols-4"
          markets={exactScoreMarkets}
          match={match}
          onSelect={onSelect}
          selectedMarketId={selectedMarketId}
          disabled={bettingDisabled}
          locale={locale}
          title={locale === "zh" ? "比分竞猜" : "Exact Score"}
        />
      </div>
    </article>
  );
}

function MarketGroup({
  gridClassName,
  markets,
  match,
  onSelect,
  selectedMarketId,
  disabled,
  title,
  locale
}: {
  gridClassName: string;
  markets: Market[];
  match: Match;
  onSelect: (selection: BetSelection) => void;
  selectedMarketId: number | null;
  disabled: boolean;
  title: string;
  locale: "en" | "zh";
}) {
  if (markets.length === 0) {
    return null;
  }

  return (
    <section>
      <h3 className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-500">{title}</h3>
      <div className={["grid gap-2", gridClassName].join(" ")}>
        {markets.map((market) => (
          <button
            key={market.id}
            className={[
              "min-h-16 rounded-md border px-2 py-2 text-center transition",
              selectedMarketId === market.id
                ? "border-emerald-700 bg-emerald-50 text-emerald-800"
                : disabled
                  ? "cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400"
                  : "border-blue-300 bg-white text-ocean hover:bg-blue-50"
            ].join(" ")}
            onClick={() => {
              if (disabled) {
                return;
              }
              onSelect({ match, market });
            }}
            disabled={disabled}
            type="button"
          >
            <span className="block text-xs font-bold uppercase text-slate-500">{getSelectionLabel(market.selection, locale)}</span>
            <span className="mt-1 block text-base font-bold">{market.odds}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
