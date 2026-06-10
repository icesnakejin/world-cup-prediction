import { useI18n } from "../context/I18nContext";

export function LanguageSwitcher({ variant = "dark" }: { variant?: "dark" | "light" }) {
  const { locale, setLocale } = useI18n();
  const isLight = variant === "light";

  return (
    <div className={["inline-flex rounded-md p-1 text-xs font-bold", isLight ? "border border-line bg-slate-50" : "border border-blue-200 bg-white/10"].join(" ")}>
      <button
        className={[
          "rounded-md px-2 py-1 transition",
          locale === "en"
            ? isLight
              ? "bg-white text-ocean"
              : "bg-white text-ocean"
            : isLight
              ? "text-slate-600 hover:text-ink"
              : "text-blue-100 hover:text-white"
        ].join(" ")}
        onClick={() => setLocale("en")}
        type="button"
      >
        EN
      </button>
      <button
        className={[
          "rounded-md px-2 py-1 transition",
          locale === "zh"
            ? isLight
              ? "bg-white text-ocean"
              : "bg-white text-ocean"
            : isLight
              ? "text-slate-600 hover:text-ink"
              : "text-blue-100 hover:text-white"
        ].join(" ")}
        onClick={() => setLocale("zh")}
        type="button"
      >
        中文
      </button>
    </div>
  );
}
