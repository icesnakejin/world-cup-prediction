import { FormEvent, useMemo, useState } from "react";
import { Send, X } from "lucide-react";

import { Match, Market } from "../api/types";
import { getMatchTitle } from "../utils/matchDisplay";

export type BetSelection = {
  match: Match;
  market: Market;
};

type BetSlipProps = {
  selection: BetSelection | null;
  onClear: () => void;
  onPlaceBet: (stake: number) => Promise<void>;
};

export function BetSlip({ selection, onClear, onPlaceBet }: BetSlipProps) {
  const [stake, setStake] = useState("100");
  const [submitting, setSubmitting] = useState(false);
  const odds = selection ? Number(selection.market.odds) : 0;
  const stakeNumber = Number(stake || 0);
  const payout = useMemo(() => (stakeNumber > 0 ? stakeNumber * odds : 0), [stakeNumber, odds]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!selection || stakeNumber <= 0) {
      return;
    }
    setSubmitting(true);
    try {
      await onPlaceBet(stakeNumber);
      setStake("100");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="rounded-md border border-line bg-white shadow-sm lg:sticky lg:top-24">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <h2 className="text-sm font-bold uppercase tracking-wide text-slate-600">Bet Slip</h2>
        {selection && (
          <button className="rounded-md p-1 text-slate-500 hover:bg-slate-100" onClick={onClear} type="button">
            <X size={18} />
          </button>
        )}
      </div>
      {!selection ? (
        <div className="p-6 text-center">
          <div className="mx-auto mb-3 grid h-16 w-16 place-items-center rounded-full bg-slate-100 text-slate-400">
            <Send size={24} />
          </div>
          <p className="text-sm font-bold text-slate-700">Bet slip empty</p>
          <p className="mt-1 text-sm text-slate-500">Select a market to place a prediction</p>
        </div>
      ) : (
        <form className="space-y-4 p-4" onSubmit={handleSubmit}>
          <div>
            <p className="text-sm font-bold text-ink">
              {getMatchTitle(selection.match)}
            </p>
            <p className="mt-1 text-xs font-semibold uppercase text-slate-500">{selection.market.selection}</p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-xs font-bold uppercase text-slate-500">Odds</p>
              <p className="mt-1 text-base font-bold text-ocean">{selection.market.odds}</p>
            </div>
            <div className="rounded-md bg-slate-50 p-3">
              <p className="text-xs font-bold uppercase text-slate-500">Payout</p>
              <p className="mt-1 text-base font-bold text-emerald-700">{payout.toFixed(0)}</p>
            </div>
          </div>
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
          <button
            className="flex h-11 w-full items-center justify-center gap-2 rounded-md bg-emerald-700 text-sm font-bold text-white hover:bg-emerald-800 disabled:opacity-60"
            disabled={submitting || stakeNumber <= 0}
            type="submit"
          >
            <Send size={17} />
            {submitting ? "Placing bet" : "Place Bet"}
          </button>
        </form>
      )}
    </section>
  );
}
