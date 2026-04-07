import type { EligibilityResult } from "../types";

interface Props {
  results: EligibilityResult[];
}

export default function EligibilityResults({ results }: Props) {
  if (results.length === 0) return null;

  return (
    <div data-testid="eligibility-results" className="space-y-4">
      <h3 className="text-lg font-bold text-blue-900">Screening Results</h3>

      {results.map((r, idx) => (
        <div
          key={idx}
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-5"
        >
          <div className="flex items-center gap-3 mb-3">
            <span
              className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-white text-sm font-bold ${
                r.likely_eligible ? "bg-green-500" : "bg-red-500"
              }`}
              aria-label={r.likely_eligible ? "Likely eligible" : "Likely not eligible"}
            >
              {r.likely_eligible ? "✓" : "✗"}
            </span>
            <div>
              <p className="font-semibold text-blue-900">{r.program}</p>
              <p className="text-xs text-gray-500">
                {Math.round(r.confidence * 100)}% confidence
              </p>
            </div>
          </div>

          {/* Confidence bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4" role="progressbar" aria-valuenow={Math.round(r.confidence * 100)} aria-valuemin={0} aria-valuemax={100}>
            <div
              className={`h-2 rounded-full ${
                r.likely_eligible ? "bg-green-500" : "bg-red-400"
              }`}
              style={{ width: `${Math.round(r.confidence * 100)}%` }}
            />
          </div>

          {r.factors.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Factors
              </p>
              <ul className="space-y-1">
                {r.factors.map((f, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-1.5">
                    <span className="text-blue-400 mt-0.5">•</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {r.next_steps.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Next Steps
              </p>
              <ol className="space-y-1 list-decimal list-inside">
                {r.next_steps.map((step, i) => (
                  <li key={i} className="text-sm text-gray-700">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
