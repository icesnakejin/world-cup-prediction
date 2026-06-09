import { Clock } from "lucide-react";

import { Match, Market } from "../api/types";
import { BetSelection } from "./BetSlip";

type MatchCardProps = {
  match: Match;
  markets: Market[];
  selectedMarketId: number | null;
  onSelect: (selection: BetSelection) => void;
};

const labels: Record<string, string> = {
  HOME_WIN: "Home",
  DRAW: "Draw",
  AWAY_WIN: "Away",
  OVER: "Over",
  UNDER: "Under"
};

export function MatchCard({ match, markets, selectedMarketId, onSelect }: MatchCardProps) {
  const teamWinMarkets = markets.filter((market) => market.market_type === "match_winner");
  const overUnderMarkets = markets.filter((market) => market.market_type === "over_under");
  const exactScoreMarkets = markets.filter((market) => market.market_type === "exact_score");

  return (
    <article className="rounded-md border border-line bg-white shadow-sm">
      <div className="border-b border-line px-4 py-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-base font-bold text-ink">
              {match.home_team} vs {match.away_team}
            </h2>
            <p className="mt-1 flex items-center gap-1 text-xs font-semibold text-slate-500">
              <Clock size={14} />
              {new Date(match.kickoff_time).toLocaleString()}
            </p>
          </div>
          <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
            {match.status}
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
          title="Team Win"
        />
        <MarketGroup
          gridClassName="grid-cols-2"
          markets={overUnderMarkets}
          match={match}
          onSelect={onSelect}
          selectedMarketId={selectedMarketId}
          title={overUnderMarkets[0]?.line ? `Over/Under ${Number(overUnderMarkets[0].line).toFixed(1)}` : "Over/Under"}
        />
        <MarketGroup
          gridClassName="grid-cols-2 sm:grid-cols-4"
          markets={exactScoreMarkets}
          match={match}
          onSelect={onSelect}
          selectedMarketId={selectedMarketId}
          title="Exact Score"
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
  title
}: {
  gridClassName: string;
  markets: Market[];
  match: Match;
  onSelect: (selection: BetSelection) => void;
  selectedMarketId: number | null;
  title: string;
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
                : "border-blue-300 bg-white text-ocean hover:bg-blue-50"
            ].join(" ")}
            onClick={() => onSelect({ match, market })}
            type="button"
          >
            <span className="block text-xs font-bold uppercase text-slate-500">{labels[market.selection] ?? market.selection}</span>
            <span className="mt-1 block text-base font-bold">{market.odds}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
