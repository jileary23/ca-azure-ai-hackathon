import { useState, useEffect, FormEvent } from "react";
import { getAgencies, searchDocuments } from "../api/apiClient";
import type { DocumentResult } from "../types";

interface Props {
  onResults: (results: DocumentResult[]) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string | null) => void;
}

export default function SearchBar({ onResults, onLoading, onError }: Props) {
  const [query, setQuery] = useState("");
  const [agency, setAgency] = useState("");
  const [agencies, setAgencies] = useState<string[]>([]);

  useEffect(() => {
    getAgencies()
      .then(setAgencies)
      .catch(() => setAgencies([]));
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    onLoading(true);
    onError(null);
    try {
      const results = await searchDocuments(trimmed, agency || undefined);
      onResults(results);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Search failed");
      onResults([]);
    } finally {
      onLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      data-testid="search-bar"
      className="flex flex-col sm:flex-row gap-2"
    >
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documents across agencies..."
        data-testid="search-input"
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
        aria-label="Search documents"
      />
      <select
        value={agency}
        onChange={(e) => setAgency(e.target.value)}
        data-testid="agency-filter"
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
        aria-label="Filter by agency"
      >
        <option value="">All Agencies</option>
        {agencies.map((a) => (
          <option key={a} value={a}>
            {a}
          </option>
        ))}
      </select>
      <button
        type="submit"
        disabled={!query.trim()}
        data-testid="search-submit"
        className="bg-amber-500 hover:bg-amber-600 text-white rounded-lg px-5 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Search
      </button>
    </form>
  );
}
