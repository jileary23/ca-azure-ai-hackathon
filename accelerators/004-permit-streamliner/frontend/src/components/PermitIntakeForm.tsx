import { useState, FormEvent } from "react";
import { classifyProject } from "../api/apiClient";

const PROJECT_TYPES = [
  { value: "residential_addition", label: "Residential Addition" },
  { value: "commercial_renovation", label: "Commercial Renovation" },
  { value: "new_construction", label: "New Construction" },
  { value: "solar_installation", label: "Solar Installation" },
  { value: "adu", label: "Accessory Dwelling Unit (ADU)" },
  { value: "other", label: "Other" },
] as const;

interface ClassificationResult {
  permit_type: string;
  requirements: string[];
  estimated_timeline: string;
  agency: string;
  notes?: string;
}

export default function PermitIntakeForm() {
  const [description, setDescription] = useState("");
  const [projectType, setProjectType] = useState("");
  const [address, setAddress] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClassificationResult | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await classifyProject({
        project_description: description.trim(),
        project_type: projectType || undefined,
        address: address.trim() || undefined,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Classification failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <form
        onSubmit={handleSubmit}
        data-testid="permit-intake-form"
        className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4"
      >
        <h3 className="text-lg font-semibold" style={{ color: "#1B2A4A" }}>
          Classify Your Project
        </h3>

        <div>
          <label
            htmlFor="project-description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Project Description *
          </label>
          <textarea
            id="project-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your project (e.g., 'Adding a 500 sq ft second-story bedroom above the garage')"
            rows={3}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 resize-none"
            data-testid="intake-description"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="project-type"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Project Type
            </label>
            <select
              id="project-type"
              value={projectType}
              onChange={(e) => setProjectType(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 bg-white"
              data-testid="intake-project-type"
            >
              <option value="">Select type...</option>
              {PROJECT_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              htmlFor="project-address"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Project Address
            </label>
            <input
              id="project-address"
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="123 Main St, Sacramento, CA"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
              data-testid="intake-address"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !description.trim()}
          data-testid="intake-submit"
          className="text-white rounded-lg px-5 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
          style={{ backgroundColor: "#D4A537" }}
        >
          {isLoading ? "Classifying..." : "Classify Project"}
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
          data-testid="intake-result"
        >
          <h4 className="text-md font-semibold mb-4" style={{ color: "#1B2A4A" }}>
            Classification Result
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                Permit Type
              </p>
              <p
                className="font-medium rounded-full inline-block px-3 py-1 text-white text-xs"
                style={{ backgroundColor: "#1B2A4A" }}
              >
                {result.permit_type}
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                Estimated Timeline
              </p>
              <p className="font-medium text-gray-900">
                {result.estimated_timeline}
              </p>
            </div>
            {result.agency && (
              <div>
                <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                  Routing Agency
                </p>
                <p className="font-medium text-gray-900">{result.agency}</p>
              </div>
            )}
          </div>

          {result.requirements && result.requirements.length > 0 && (
            <div className="mt-4">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">
                Requirements
              </p>
              <ul className="space-y-1">
                {result.requirements.map((req, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-gray-700"
                  >
                    <span
                      className="mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: "#D4A537" }}
                    />
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.notes && (
            <p className="mt-3 text-xs text-gray-500 italic">{result.notes}</p>
          )}
        </div>
      )}
    </div>
  );
}
