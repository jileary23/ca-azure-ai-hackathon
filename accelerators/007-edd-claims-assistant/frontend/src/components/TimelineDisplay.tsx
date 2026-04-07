import { useEffect, useState } from "react";
import type { TimelineStep } from "../types";
import { getTimeline } from "../api/apiClient";

interface Props {
  claimType: string;
}

export default function TimelineDisplay({ claimType }: Props) {
  const [steps, setSteps] = useState<TimelineStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getTimeline(claimType);
        if (!cancelled) setSteps(Array.isArray(data) ? data : data.steps ?? []);
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [claimType]);

  if (loading) {
    return (
      <div className="text-center py-8 text-sm text-gray-500">
        Loading timeline…
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

  if (steps.length === 0) return null;

  return (
    <div
      data-testid="timeline-display"
      className="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
    >
      <h3 className="text-lg font-semibold text-blue-900 mb-4">
        Claim Processing Timeline
      </h3>
      <div className="relative">
        {/* vertical connector line */}
        <div className="absolute left-4 top-3 bottom-3 w-0.5 bg-blue-200" />

        <div className="space-y-6">
          {steps.map((step, i) => (
            <div key={i} className="relative flex gap-4">
              {/* dot */}
              <div className="relative z-10 flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                {i + 1}
              </div>

              {/* content */}
              <div className="flex-1 pb-1">
                <div className="flex items-baseline gap-2">
                  <span className="font-medium text-gray-900 text-sm">
                    {step.step_name}
                  </span>
                  <span className="text-xs text-blue-600 font-medium">
                    ~{step.estimated_days} day{step.estimated_days !== 1 ? "s" : ""}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-0.5">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}