import { useState, FormEvent } from "react";
import { prescreenEligibility } from "../api/apiClient";
import type { EligibilityResult } from "../types";

interface Props {
  onResults: (results: EligibilityResult[]) => void;
}

export default function EligibilityForm({ onResults }: Props) {
  const [householdSize, setHouseholdSize] = useState<number>(1);
  const [monthlyIncome, setMonthlyIncome] = useState<number>(0);
  const [county, setCounty] = useState("");
  const [hasChildren, setHasChildren] = useState(false);
  const [age, setAge] = useState<number | "">("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!county.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const data = await prescreenEligibility({
        household_size: householdSize,
        monthly_income: monthlyIncome,
        county: county.trim(),
        has_children: hasChildren,
        ...(age !== "" ? { age: Number(age) } : {}),
      });

      const results: EligibilityResult[] = Array.isArray(data.results)
        ? data.results
        : Array.isArray(data)
          ? data
          : [data];
      onResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Screening failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      data-testid="eligibility-form"
      className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-5"
    >
      <h3 className="text-lg font-bold text-blue-900">
        Eligibility Pre-Screening
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="household-size"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Household Size
          </label>
          <input
            id="household-size"
            type="number"
            min={1}
            value={householdSize}
            onChange={(e) => setHouseholdSize(Number(e.target.value))}
            aria-label="Household size"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="monthly-income"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Monthly Income ($)
          </label>
          <input
            id="monthly-income"
            type="number"
            min={0}
            value={monthlyIncome}
            onChange={(e) => setMonthlyIncome(Number(e.target.value))}
            aria-label="Monthly income"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="county"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            County
          </label>
          <input
            id="county"
            type="text"
            value={county}
            onChange={(e) => setCounty(e.target.value)}
            placeholder="e.g. Los Angeles"
            required
            aria-label="County"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="age"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Age (optional)
          </label>
          <input
            id="age"
            type="number"
            min={0}
            value={age}
            onChange={(e) =>
              setAge(e.target.value === "" ? "" : Number(e.target.value))
            }
            aria-label="Age"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          id="has-children"
          type="checkbox"
          checked={hasChildren}
          onChange={(e) => setHasChildren(e.target.checked)}
          aria-label="Has children"
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="has-children" className="text-sm text-gray-700">
          Household includes children under 18
        </label>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting || !county.trim()}
        data-testid="eligibility-submit"
        className="w-full bg-yellow-400 hover:bg-yellow-500 text-blue-900 font-semibold rounded-lg px-4 py-2.5 text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? "Checking…" : "Check Eligibility"}
      </button>
    </form>
  );
}
