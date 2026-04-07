import { useState, FormEvent } from "react";
import type { ClaimStatus } from "../types";
import { lookupClaimStatus } from "../api/apiClient";

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 border-green-200",
  pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
  denied: "bg-red-100 text-red-800 border-red-200",
  exhausted: "bg-gray-100 text-gray-800 border-gray-200",
  on_hold: "bg-orange-100 text-orange-800 border-orange-200",
};

export default function ClaimStatusForm() {
  const [claimId, setClaimId] = useState("");
  const [ssnLast4, setSsnLast4] = useState("");
  const [lastName, setLastName] = useState("");
  const [result, setResult] = useState<ClaimStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasIdentifier = claimId.trim() || ssnLast4.trim() || lastName.trim();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!hasIdentifier) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params: Record<string, string> = {};
      if (claimId.trim()) params.claim_id = claimId.trim();
      if (ssnLast4.trim()) params.ssn_last4 = ssnLast4.trim();
      if (lastName.trim()) params.last_name = lastName.trim();

      const data = await lookupClaimStatus(params);
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
        data-testid="claim-status-form"
        className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4"
      >
        <h3 className="text-lg font-semibold text-blue-900">
          Look Up Claim Status
        </h3>
        <p className="text-sm text-gray-500">
          Enter at least one identifier to look up your claim.
        </p>

        <div className="space-y-3">
          <div>
            <label
              htmlFor="claim-id"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Claim ID
            </label>
            <input
              id="claim-id"
              type="text"
              value={claimId}
              onChange={(e) => setClaimId(e.target.value)}
              placeholder="e.g. UI-2024-123456"
              className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              data-testid="claim-id-input"
            />
          </div>

          <div>
            <label
              htmlFor="ssn-last4"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Last 4 of SSN
            </label>
            <input
              id="ssn-last4"
              type="text"
              value={ssnLast4}
              onChange={(e) => {
                const v = e.target.value.replace(/\D/g, "").slice(0, 4);
                setSsnLast4(v);
              }}
              placeholder="1234"
              maxLength={4}
              inputMode="numeric"
              className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              data-testid="ssn-last4-input"
            />
          </div>

          <div>
            <label
              htmlFor="last-name"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Last Name
            </label>
            <input
              id="last-name"
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Smith"
              className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              data-testid="last-name-input"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={!hasIdentifier || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="claim-submit"
        >
          {loading ? "Looking up…" : "Look Up Claim"}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
          {error}
        </div>
      )}

      {result && (
        <div
          data-testid="claim-result"
          className="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <h3 className="text-lg font-semibold text-blue-900">
              {result.claim_type} Claim
            </h3>
            <span
              className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
                STATUS_COLORS[result.status] || "bg-gray-100 text-gray-800"
              }`}
            >
              {result.status}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500 block text-xs">Claim ID</span>
              <span className="font-medium text-gray-900">
                {result.claim_id}
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-xs">Filed Date</span>
              <span className="font-medium text-gray-900">
                {new Date(result.filed_date).toLocaleDateString()}
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-xs">
                Weekly Benefit
              </span>
              <span className="font-medium text-blue-700 text-lg">
                ${result.weekly_benefit_amount.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="text-gray-500 block text-xs">
                Remaining Balance
              </span>
              <span className="font-medium text-gray-900">
                ${result.remaining_balance.toFixed(2)}
              </span>
            </div>
            {result.next_payment_date && (
              <div>
                <span className="text-gray-500 block text-xs">
                  Next Payment
                </span>
                <span className="font-medium text-gray-900">
                  {new Date(result.next_payment_date).toLocaleDateString()}
                </span>
              </div>
            )}
            {result.last_certified && (
              <div>
                <span className="text-gray-500 block text-xs">
                  Last Certified
                </span>
                <span className="font-medium text-gray-900">
                  {new Date(result.last_certified).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>

          {result.pending_issues.length > 0 && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm font-medium text-red-800 mb-1">
                Pending Issues
              </p>
              <ul className="space-y-1">
                {result.pending_issues.map((issue, i) => (
                  <li key={i} className="text-sm text-red-700 flex gap-2">
                    <span>⚠</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}