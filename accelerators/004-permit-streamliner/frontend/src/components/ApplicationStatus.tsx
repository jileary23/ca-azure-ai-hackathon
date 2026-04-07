import { Fragment, useEffect, useState } from "react";
import { getApplications } from "../api/apiClient";
import type { PermitApplication } from "../types";

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string; step: number }> = {
  submitted: { color: "text-blue-700", bg: "bg-blue-100", label: "Submitted", step: 1 },
  in_review: { color: "text-yellow-700", bg: "bg-yellow-100", label: "In Review", step: 2 },
  approved: { color: "text-green-700", bg: "bg-green-100", label: "Approved", step: 3 },
  denied: { color: "text-red-700", bg: "bg-red-100", label: "Denied", step: 3 },
};

const STEPS = ["Submitted", "In Review", "Decision"];

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? {
    color: "text-gray-700",
    bg: "bg-gray-100",
    label: status,
    step: 0,
  };
  return (
    <span
      className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${cfg.color} ${cfg.bg}`}
    >
      {cfg.label}
    </span>
  );
}

function ProgressBar({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status];
  const currentStep = cfg?.step ?? 0;

  return (
    <div className="flex items-center gap-1 mt-3">
      {STEPS.map((label, i) => {
        const stepNum = i + 1;
        const reached = stepNum <= currentStep;
        const isDenied = status === "denied" && stepNum === 3;
        return (
          <Fragment key={label}>
            {i > 0 && (
              <div
                className="flex-1 h-0.5 rounded"
                style={{
                  backgroundColor: reached ? (isDenied ? "#EF4444" : "#D4A537") : "#E5E7EB",
                }}
              />
            )}
            <div className="flex flex-col items-center">
              <div
                className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                style={{
                  backgroundColor: reached
                    ? isDenied
                      ? "#EF4444"
                      : "#D4A537"
                    : "#D1D5DB",
                }}
              >
                {stepNum}
              </div>
              <span className="text-[9px] text-gray-400 mt-0.5">{label}</span>
            </div>
          </Fragment>
        );
      })}
    </div>
  );
}

export default function ApplicationStatus() {
  const [applications, setApplications] = useState<PermitApplication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getApplications();
        if (!cancelled) {
          setApplications(Array.isArray(data) ? data : data.applications ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load applications");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
        <div className="flex justify-center gap-1">
          <span className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: "#D4A537" }} />
          <span className="w-2 h-2 rounded-full animate-bounce [animation-delay:0.1s]" style={{ backgroundColor: "#D4A537" }} />
          <span className="w-2 h-2 rounded-full animate-bounce [animation-delay:0.2s]" style={{ backgroundColor: "#D4A537" }} />
        </div>
        <p className="text-sm text-gray-500 mt-2">Loading applications...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  if (applications.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 text-center">
        <p className="text-gray-500 text-sm">No applications found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="application-status">
      <h3 className="text-lg font-semibold" style={{ color: "#1B2A4A" }}>
        Your Applications
      </h3>
      {applications.map((app) => (
        <div
          key={app.app_id}
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-5"
          data-testid={`app-card-${app.app_id}`}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs text-gray-400 font-mono">{app.app_id}</p>
              <p className="text-sm font-medium text-gray-900 mt-0.5 truncate">
                {app.project_description || app.project_type}
              </p>
              {app.address && (
                <p className="text-xs text-gray-500 mt-0.5">📍 {app.address}</p>
              )}
            </div>
            <StatusBadge status={app.status} />
          </div>
          <ProgressBar status={app.status} />
          {app.estimated_completion && (
            <p className="text-xs text-gray-400 mt-2">
              Est. completion: {app.estimated_completion}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
