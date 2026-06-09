import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trophy } from "lucide-react";

import { api } from "../api/client";
import { Tournament } from "../api/types";
import { EmptyState } from "../components/EmptyState";

export function TournamentsPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTournaments() {
      const response = await api.get<Tournament[]>("/tournaments");
      setTournaments(response.data);
      setLoading(false);
    }

    void loadTournaments();
  }, []);

  return (
    <section className="space-y-3">
      <div className="rounded-md border border-line bg-white px-4 py-3 shadow-sm">
        <h1 className="text-lg font-bold text-ink">Tournaments</h1>
        <p className="text-sm text-slate-500">Tournament winner futures use virtual coins only.</p>
      </div>
      {loading && <EmptyState title="Loading tournaments" />}
      {!loading && tournaments.length === 0 && <EmptyState title="No tournaments available" />}
      <div className="grid gap-3 md:grid-cols-2">
        {tournaments.map((tournament) => (
          <Link
            className="rounded-md border border-line bg-white p-4 shadow-sm transition hover:border-blue-300 hover:shadow-md"
            key={tournament.id}
            to={`/tournaments/${tournament.id}`}
          >
            <div className="flex items-start gap-3">
              <div className="grid h-11 w-11 place-items-center rounded-md bg-blue-50 text-ocean">
                <Trophy size={22} />
              </div>
              <div className="min-w-0">
                <h2 className="font-bold text-ink">{tournament.name}</h2>
                <p className="mt-1 text-sm text-slate-500">{tournament.year}</p>
                <span className="mt-3 inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-bold uppercase text-slate-600">
                  {tournament.status}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
