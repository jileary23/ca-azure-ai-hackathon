import { useEffect, useState } from "react";
import { getAlerts } from "../api/apiClient";
import type { EmergencyAlert } from "../types";

const SEV_COLORS: Record<string, string> = {
  extreme: "bg-red-700 text-white border-red-900",
  severe: "bg-orange-600 text-white border-orange-800",
  moderate: "bg-yellow-500 text-gray-900 border-yellow-600",
  minor: "bg-blue-400 text-white border-blue-600",
};

interface Props {
  zip?: string;
}

export default function AlertCards({ zip }: Props) {
  const [alerts, setAlerts] = useState<EmergencyAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getAlerts(zip)
      .then((data) => {
        if (!cancelled) setAlerts(Array.isArray(data) ? data : data.alerts ?? []);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load alerts");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [zip]);

  if (loading) {
    return (
      <div data-testid="alert-cards" className="animate-pulse text-gray-400 text-sm p-3">
        Loading alerts…
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="alert-cards" className="text-red-400 text-sm p-3">
        ⚠️ {error}
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div data-testid="alert-cards" className="text-gray-500 text-sm p-3">
        No active alerts{zip ? ` for ${zip}` : ""}.
      </div>
    );
  }

  return (
    <div data-testid="alert-cards" className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.alert_id}
          className={`rounded-lg p-3 border ${SEV_COLORS[alert.severity] ?? "bg-gray-600 text-white border-gray-700"}`}
        >
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wide">
              ⚠️ {alert.severity}
            </span>
            <span className="text-xs opacity-75">{alert.emergency_type}</span>
          </div>
          <p className="font-semibold text-sm mt-1">{alert.title}</p>
          <p className="text-xs mt-1 opacity-90">{alert.description}</p>
          {alert.affected_areas.length > 0 && (
            <p className="text-xs mt-1 opacity-75">
              Areas: {alert.affected_areas.join(", ")}
            </p>
          )}
          {alert.instructions && (
            <p className="text-xs mt-2 italic opacity-90">📋 {alert.instructions}</p>
          )}
        </div>
      ))}
    </div>
  );
}
