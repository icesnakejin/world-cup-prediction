import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { AuthCard } from "../components/AuthCard";
import { useAuth } from "../context/AuthContext";
import { useI18n } from "../context/I18nContext";

export function RegisterPage() {
  const { register } = useAuth();
  const { t } = useI18n();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await register(username, email, password);
    } catch {
      setError(t("registrationFailed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthCard title={t("register")} subtitle={t("startWithVirtualCoins")}>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <label className="block text-sm font-semibold text-slate-700">
          {t("username")}
          <input
            className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
            onChange={(event) => setUsername(event.target.value)}
            value={username}
          />
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          {t("email")}
          <input
            className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            value={email}
          />
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          {t("password")}
          <input
            className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            value={password}
          />
        </label>
        {error && <p className="text-sm font-semibold text-red-600">{error}</p>}
        <button className="h-11 w-full rounded-md bg-ocean text-sm font-bold text-white hover:bg-blue-800" disabled={submitting} type="submit">
          {submitting ? t("creatingAccount") : t("createAccount")}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-slate-600">
        {t("alreadyRegistered")}{" "}
        <Link className="font-bold text-ocean" to="/login">
          {t("signIn")}
        </Link>
      </p>
    </AuthCard>
  );
}
