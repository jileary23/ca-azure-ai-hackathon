import { useEffect, useState } from "react";
import { getShelters } from "../api/apiClient";
import type { ShelterInfo } from "../types";

interface Props {
  zip?: string;
}

export default function ShelterList({ zip }: Props) {
  const [shelters, setShelters] = useState<ShelterInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getShelters(zip)
      .then((data) => {
        if (!cancelled) setShelters(Array.isArray(data) ? data : data.shelters ?? []);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load shelters");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [zip]);

  if (loading) {
    return (
      <div data-testid="shelter-list" className="animate-pulse text-gray-400 text-sm p-3">
        Loading shelters…
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="shelter-list" className="text-red-400 text-sm p-3">
        ⚠️ {error}
      </div>
    );
  }

  if (shelters.length === 0) {
    return (
      <div data-testid="shelter-list" className="text-gray-500 text-sm p-3">
        No shelters found{zip ? ` near ${zip}` : ""}.
      </div>
    );
  }

  return (
    <div data-testid="shelter-list" className="space-y-2">
      {shelters.map((s) => {
        const occupancyPct = s.capacity > 0 ? (s.current_occupancy / s.capacity) * 100 : 0;
        const barColor =
          occupancyPct >= 90 ? "bg-red-500" : occupancyPct >= 70 ? "bg-yellow-500" : "bg-green-500";

        return (
          <div key={s.shelter_id} className="bg-gray-800 border border-gray-700 rounded-lg p-3">
            <p className="font-semibold text-sm text-gray-100">{s.name}</p>
            <p className="text-xs text-gray-400">
              {s.address}, {s.city} · {s.status}
            </p>

            {/* Capacity bar */}
            <div className="mt-2">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Capacity</span>
                <span>
                  {s.current_occupancy}/{s.capacity}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`${barColor} h-2 rounded-full transition-all`}
                  style={{ width: `${Math.min(occupancyPct, 100)}%` }}
                />
              </div>
            </div>

            <div className="flex gap-3 mt-2 text-xs text-gray-400">
              {s.accepts_pets && <span>🐾 Pets OK</span>}
              {s.ada_accessible && <span>♿ ADA</span>}
              {s.distance_miles != null && <span>📍 {s.distance_miles.toFixed(1)} mi</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
