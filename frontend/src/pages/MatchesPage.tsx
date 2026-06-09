import { useEffect, useState } from "react";

import { api } from "../api/client";
import { MatchMarket, Match, Market } from "../api/types";
import { BetSelection, BetSlip } from "../components/BetSlip";
import { EmptyState } from "../components/EmptyState";
import { MatchCard } from "../components/MatchCard";
import { useToast } from "../context/ToastContext";
import { formatStage } from "../utils/matchDisplay";

type MarketMap = Record<number, Market[]>;

const STAGE_ORDER = ["group", "round_of_32", "round_of_16", "quarter_final", "semi_final", "third_place", "final"];

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
          const allMarketsResponse = await api.get<MatchMarket[]>("/matches/all-markets");
          setMatches(matchResponse.data);
          const grouped: MarketMap = {};
          for (const market of allMarketsResponse.data) {
            if (!grouped[market.match_id]) {
              grouped[market.match_id] = [];
            }
            grouped[market.match_id].push(market);
          }
          setMarketsByMatch(grouped);
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

  const sections = buildMatchSections(matches);

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
          sections.map((section) => (
            <section key={section.title} className="space-y-3">
              <h2 className="px-1 text-sm font-bold uppercase tracking-wide text-slate-500">{section.title}</h2>
              {section.matches.map((match) => (
                <MatchCard
                  key={match.id}
                  match={match}
                  markets={marketsByMatch[match.id] ?? []}
                  onSelect={setSelected}
                  selectedMarketId={selected?.market.id ?? null}
                />
              ))}
            </section>
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

function buildMatchSections(matches: Match[]) {
  const sorted = [...matches].sort((left, right) => {
    const leftStage = STAGE_ORDER.indexOf(left.stage ?? "");
    const rightStage = STAGE_ORDER.indexOf(right.stage ?? "");
    const leftStageOrder = leftStage === -1 ? STAGE_ORDER.length : leftStage;
    const rightStageOrder = rightStage === -1 ? STAGE_ORDER.length : rightStage;
    if (leftStageOrder !== rightStageOrder) {
      return leftStageOrder - rightStageOrder;
    }
    return (left.match_number ?? 9999) - (right.match_number ?? 9999);
  });

  const sections: { title: string; matches: Match[] }[] = [];
  const byTitle = new Map<string, Match[]>();

  for (const match of sorted) {
    const title = match.stage === "group" && match.group ? `Group ${match.group}` : formatStage(match.stage);
    if (!byTitle.has(title)) {
      byTitle.set(title, []);
      sections.push({ title, matches: byTitle.get(title)! });
    }
    byTitle.get(title)!.push(match);
  }

  return sections;
}
