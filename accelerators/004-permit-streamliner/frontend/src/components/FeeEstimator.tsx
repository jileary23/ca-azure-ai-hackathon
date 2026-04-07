import { useState, FormEvent } from "react";
import { estimateFees } from "../api/apiClient";

const PROJECT_TYPES = [
  { value: "residential_addition", label: "Residential Addition" },
  { value: "commercial_renovation", label: "Commercial Renovation" },
  { value: "new_construction", label: "New Construction" },
  { value: "solar_installation", label: "Solar Installation" },
  { value: "adu", label: "Accessory Dwelling Unit (ADU)" },
  { value: "other", label: "Other" },
] as const;

interface FeeBreakdown {
  total: number;
  items: { name: string; amount: number; description?: string }[];
  notes?: string;
}

export default function FeeEstimator() {
  const [projectType, setProjectType] = useState("");
  const [sqft, setSqft] = useState("");
  const [valuation, setValuation] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FeeBreakdown | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!projectType) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await estimateFees({
        project_type: projectType,
        square_footage: sqft ? Number(sqft) : undefined,
        valuation: valuation ? Number(valuation) : undefined,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fee estimation failed");
    } finally {
      setIsLoading(false);
    }
  };

  const formatUSD = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);

  return (
    <div className="space-y-6">
      <form
        onSubmit={handleSubmit}
        data-testid="fee-estimator"
        className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4"
      >
        <h3 className="text-lg font-semibold" style={{ color: "#1B2A4A" }}>
          Estimate Permit Fees
        </h3>

        <div>
          <label
            htmlFor="fee-project-type"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Project Type *
          </label>
          <select
            id="fee-project-type"
            value={projectType}
            onChange={(e) => setProjectType(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 bg-white"
            data-testid="fee-project-type"
          >
            <option value="">Select type...</option>
            {PROJECT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="fee-sqft"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Square Footage
            </label>
            <input
              id="fee-sqft"
              type="number"
              min="0"
              value={sqft}
              onChange={(e) => setSqft(e.target.value)}
              placeholder="e.g. 1200"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
              data-testid="fee-sqft"
            />
          </div>
          <div>
            <label
              htmlFor="fee-valuation"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Project Valuation (USD)
            </label>
            <input
              id="fee-valuation"
              type="number"
              min="0"
              value={valuation}
              onChange={(e) => setValuation(e.target.value)}
              placeholder="e.g. 150000"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
              data-testid="fee-valuation"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !projectType}
          data-testid="fee-submit"
          className="text-white rounded-lg px-5 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
          style={{ backgroundColor: "#D4A537" }}
        >
          {isLoading ? "Calculating..." : "Estimate Fees"}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
          data-testid="fee-result"
        >
          <h4 className="text-md font-semibold mb-4" style={{ color: "#1B2A4A" }}>
            Fee Breakdown
          </h4>

          {result.items && result.items.length > 0 && (
            <div className="space-y-2 mb-4">
              {result.items.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm py-1.5 border-b border-gray-100 last:border-0"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-900">{item.name}</p>
                    {item.description && (
                      <p className="text-xs text-gray-400">{item.description}</p>
                    )}
                  </div>
                  <span className="font-medium text-gray-700 ml-4 flex-shrink-0">
                    {formatUSD(item.amount)}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div
            className="flex items-center justify-between pt-3 border-t-2"
            style={{ borderColor: "#D4A537" }}
          >
            <span className="text-sm font-semibold" style={{ color: "#1B2A4A" }}>
              Total Estimated Fees
            </span>
            <span className="text-lg font-bold" style={{ color: "#1B2A4A" }}>
              {formatUSD(result.total)}
            </span>
          </div>

          {result.notes && (
            <p className="mt-3 text-xs text-gray-500 italic">{result.notes}</p>
          )}
        </div>
      )}
    </div>
  );
}
