import { useState, FormEvent } from "react";
import type { BenefitCalculation } from "../types";
import { calculateBenefits } from "../api/apiClient";

const CLAIM_TYPES = [
  { value: "ui", label: "Unemployment Insurance" },
  { value: "di", label: "Disability Insurance" },
  { value: "pfl", label: "Paid Family Leave" },
];

const QUARTER_LABELS = ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"];

export default function BenefitCalculator() {
  const [claimType, setClaimType] = useState("ui");
  const [wages, setWages] = useState(["", "", "", ""]);
  const [result, setResult] = useState<BenefitCalculation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateWage = (index: number, value: string) => {
    const next = [...wages];
    next[index] = value;
    setWages(next);
  };

  const hasWages = wages.some((w) => w.trim() !== "" && Number(w) > 0);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!hasWages) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const quarterly_wages = wages.map((w) => {
        const n = Number(w);
        return isNaN(n) ? 0 : n;
      });

      const data = await calculateBenefits({
        claim_type: claimType,
        quarterly_wages,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <form
        onSubmit={handleSubmit}
        data-testid="benefit-calculator"
        className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4"
      >
        <h3 className="text-lg font-semibold text-blue-900">
          Benefit Calculator
        </h3>
        <p className="text-sm text-gray-500">
          Estimate your weekly benefit amount based on quarterly wages.
        </p>

        <div>
          <label
            htmlFor="claim-type"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Claim Type
          </label>
          <select
            id="claim-type"
            value={claimType}
            onChange={(e) => setClaimType(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            data-testid="claim-type-select"
          >
            {CLAIM_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-700">Quarterly Wages</p>
          {QUARTER_LABELS.map((label, i) => (
            <div key={i}>
              <label
                htmlFor={`wage-q${i}`}
                className="block text-xs text-gray-500 mb-0.5"
              >
                {label}
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
                  $
                </span>
                <input
                  id={`wage-q${i}`}
                  type="number"
                  min="0"
                  step="0.01"
                  value={wages[i]}
                  onChange={(e) => updateWage(i, e.target.value)}
                  placeholder="0.00"
                  className="w-full rounded-lg border border-gray-300 pl-7 pr-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  data-testid={`wage-q${i}-input`}
                />
              </div>
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={!hasWages || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="calculate-submit"
        >
          {loading ? "Calculating…" : "Calculate Benefits"}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div
          data-testid="benefit-result"
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            Estimated Benefits
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <span className="block text-xs text-blue-600 font-medium uppercase tracking-wide">
                Weekly Amount
              </span>
              <span className="block text-2xl font-bold text-blue-900 mt-1">
                ${result.weekly_benefit_amount.toFixed(2)}
              </span>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <span className="block text-xs text-blue-600 font-medium uppercase tracking-wide">
                Max Benefit
              </span>
              <span className="block text-2xl font-bold text-blue-900 mt-1">
                ${result.max_benefit_amount.toFixed(2)}
              </span>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <span className="block text-xs text-blue-600 font-medium uppercase tracking-wide">
                Duration
              </span>
              <span className="block text-2xl font-bold text-blue-900 mt-1">
                {result.benefit_duration_weeks} wks
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}