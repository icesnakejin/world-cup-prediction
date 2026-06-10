import { ReactNode } from "react";
import { Trophy } from "lucide-react";

import { LanguageSwitcher } from "./LanguageSwitcher";

export function AuthCard({ children, title, subtitle }: { children: ReactNode; title: string; subtitle: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#eef3f8] px-4 py-8">
      <div className="w-full max-w-md rounded-md border border-line bg-white p-6 shadow-sm">
        <div className="mb-4 flex justify-end">
          <LanguageSwitcher variant="light" />
        </div>
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-md bg-ocean text-white">
            <Trophy size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-ink">{title}</h1>
            <p className="text-sm text-slate-500">{subtitle}</p>
          </div>
        </div>
        {children}
      </div>
    </div>
  );
}
