import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { AuthCard } from "../components/AuthCard";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email, password);
    } catch {
      setError("Invalid email or password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthCard title="Sign in" subtitle="Use your prediction league account">
      <form className="space-y-4" onSubmit={handleSubmit}>
        <label className="block text-sm font-semibold text-slate-700">
          Email
          <input
            className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            value={email}
          />
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          Password
          <input
            className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-ocean"
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            value={password}
          />
        </label>
        {error && <p className="text-sm font-semibold text-red-600">{error}</p>}
        <button className="h-11 w-full rounded-md bg-ocean text-sm font-bold text-white hover:bg-blue-800" disabled={submitting} type="submit">
          {submitting ? "Signing in" : "Sign in"}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-slate-600">
        No account?{" "}
        <Link className="font-bold text-ocean" to="/register">
          Register
        </Link>
      </p>
    </AuthCard>
  );
}
