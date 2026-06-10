import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api } from "../api/client";
import { MatchMarket, Match, Market } from "../api/types";
import { BetSelection, BetSlip } from "../components/BetSlip";
import { EmptyState } from "../components/EmptyState";
import { MatchCard } from "../components/MatchCard";
import { useI18n } from "../context/I18nContext";
import { useToast } from "../context/ToastContext";
import { formatStage } from "../utils/matchDisplay";

type MarketMap = Record<number, Market[]>;

const STAGE_ORDER = ["group", "round_of_32", "round_of_16", "quarter_final", "semi_final", "third_place", "final"];
const GROUP_ORDER = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"];

export function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [marketsByMatch, setMarketsByMatch] = useState<MarketMap>({});
  const [selected, setSelected] = useState<BetSelection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { locale, t } = useI18n();
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const activeStage = searchParams.get("stage") === "knockout" ? "knockout" : "group";

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
        setError(t("couldNotLoadMatches"));
      } finally {
        setLoading(false);
      }
    }

    void loadMatches();
  }, [t]);

  useEffect(() => {
    if (activeStage === "knockout") {
      setSelected(null);
    }
  }, [activeStage]);

  async function placeBet(stake: number) {
    if (!selected) {
      return;
    }
    await api.post("/bets", { market_id: selected.market.id, stake });
    setSelected(null);
    window.dispatchEvent(new Event("wallet:refresh"));
    showToast(locale === "zh" ? "下注成功" : "Bet placed successfully");
  }

  const sections = buildMatchSections(matches, locale);
  const groupStage = sections.filter((section) => section.kind === "group");
  const knockoutStage = sections.filter((section) => section.kind === "knockout");
  const visibleSections = activeStage === "group" ? groupStage : knockoutStage;

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
      <section className="min-w-0 space-y-3">
        <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
          <h1 className="text-lg font-bold text-ink">{t("worldCupMatches")}</h1>
          <p className="text-sm text-slate-500">
            {activeStage === "group" ? t("groupStageMatchesAndMarkets") : t("knockoutStageMatchesAndMarkets")}
          </p>
        </div>
        {loading && <EmptyState title={t("loadingMatches")} />}
        {error && <EmptyState title={error} />}
        {!loading && !error && matches.length === 0 && <EmptyState title={t("noMatchesAvailable")} />}
        {!loading && !error && matches.length > 0 && (
          <div className="space-y-4">
            {visibleSections.map((section) => (
              <details key={section.title} className="group rounded-md border border-line bg-white shadow-sm">
                <summary className="cursor-pointer list-none border-b border-line px-4 py-3">
                  <span className="flex items-center justify-between gap-3">
                    <span className="text-sm font-bold uppercase tracking-wide text-slate-500">
                      {section.title}
                    </span>
                    <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      {section.matches.length} {t("matches")}
                    </span>
                  </span>
                </summary>
                <div className="space-y-3 p-3">
                  {section.matches.map((match) => (
                    <MatchCard
                      key={match.id}
                      match={match}
                      markets={marketsByMatch[match.id] ?? []}
                      onSelect={setSelected}
                      selectedMarketId={selected?.market.id ?? null}
                    />
                  ))}
                </div>
              </details>
            ))}
          </div>
        )}
      </section>
      {activeStage === "group" && (
        <>
          <aside className="hidden xl:block">
            <BetSlip onClear={() => setSelected(null)} onPlaceBet={placeBet} selection={selected} />
          </aside>
          <div className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-[#eef3f8] p-3 shadow-2xl xl:hidden">
            <BetSlip onClear={() => setSelected(null)} onPlaceBet={placeBet} selection={selected} />
          </div>
        </>
      )}
    </div>
  );
}

function buildMatchSections(matches: Match[], locale: "en" | "zh") {
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

  const sections: { kind: "group" | "knockout"; title: string; matches: Match[] }[] = [];
  const groupMap = new Map<string, Match[]>();
  const knockoutMap = new Map<string, Match[]>();

  for (const match of sorted) {
    if (match.stage === "group") {
      const title = match.group ? (locale === "zh" ? `${match.group}组` : `Group ${match.group}`) : locale === "zh" ? "小组赛" : "Group Stage";
      if (!groupMap.has(title)) {
        groupMap.set(title, []);
        sections.push({ kind: "group", title, matches: groupMap.get(title)! });
      }
      groupMap.get(title)!.push(match);
      continue;
    }

    const title = formatStage(match.stage, locale);
    if (!knockoutMap.has(title)) {
      knockoutMap.set(title, []);
      sections.push({ kind: "knockout", title, matches: knockoutMap.get(title)! });
    }
    knockoutMap.get(title)!.push(match);
  }

  sections.sort((left, right) => {
    const leftGroup = left.kind === "group" ? left.title.replace("Group ", "").replace("组", "") : "";
    const rightGroup = right.kind === "group" ? right.title.replace("Group ", "").replace("组", "") : "";
    const leftOrder = left.kind === "group" ? GROUP_ORDER.indexOf(leftGroup) : STAGE_ORDER.indexOf(stageKey(left.title, locale));
    const rightOrder = right.kind === "group" ? GROUP_ORDER.indexOf(rightGroup) : STAGE_ORDER.indexOf(stageKey(right.title, locale));
    return (leftOrder === -1 ? 999 : leftOrder) - (rightOrder === -1 ? 999 : rightOrder);
  });

  return sections;
}

function stageKey(title: string, locale: "en" | "zh") {
  const labels: Record<string, string> = locale === "zh"
    ? {
        "1/16 决赛": "round_of_32",
        "1/8 决赛": "round_of_16",
        "1/4 决赛": "quarter_final",
        半决赛: "semi_final",
        "三四名决赛": "third_place",
        决赛: "final"
      }
    : {
        "Round of 32": "round_of_32",
        "Round of 16": "round_of_16",
        "Quarter Final": "quarter_final",
        "Semi Final": "semi_final",
        "Third Place": "third_place",
        Final: "final"
      };
  return labels[title] ?? "group";
}
