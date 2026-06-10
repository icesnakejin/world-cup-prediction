import { useEffect, useState } from "react";
import { Wallet as WalletIcon } from "lucide-react";

import { api } from "../api/client";
import { Wallet } from "../api/types";
import { useI18n } from "../context/I18nContext";

export function WalletPage() {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const { t } = useI18n();

  useEffect(() => {
    async function loadWallet() {
      const response = await api.get<Wallet>("/wallet");
      setWallet(response.data);
    }

    void loadWallet();
  }, []);

  return (
    <section className="rounded-md border border-line bg-white p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="grid h-12 w-12 place-items-center rounded-md bg-emerald-50 text-emerald-700">
          <WalletIcon size={24} />
        </div>
        <div>
          <h1 className="text-lg font-bold text-ink">{t("wallet")}</h1>
          <p className="text-sm text-slate-500">{t("virtualCoinBalance")}</p>
        </div>
      </div>
      <p className="mt-6 text-4xl font-bold text-ink">
        {wallet ? wallet.balance.toLocaleString() : "-"} {t("coins")}
      </p>
    </section>
  );
}
