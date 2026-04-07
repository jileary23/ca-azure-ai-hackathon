import type { DocumentResult } from "../types";

interface Props {
  results: DocumentResult[];
}

export default function SearchResults({ results }: Props) {
  if (results.length === 0) return null;

  return (
    <div data-testid="search-results" className="space-y-3">
      {results.map((doc) => (
        <div
          key={doc.doc_id}
          className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition"
        >
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="text-xs font-semibold bg-blue-900 text-white px-2 py-0.5 rounded">
              {doc.agency}
            </span>
            <span className="text-xs font-medium bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
              {doc.document_type}
            </span>
            {doc.department && (
              <span className="text-xs text-gray-500">{doc.department}</span>
            )}
          </div>

          <h3 className="font-semibold text-sm text-blue-900 mb-1">
            {doc.title}
          </h3>

          <p className="text-xs text-gray-600 mb-3 line-clamp-2">
            {doc.summary}
          </p>

          <div className="flex items-center gap-4">
            {/* Relevance bar */}
            <div className="flex items-center gap-2 flex-1">
              <span className="text-[10px] text-gray-500 whitespace-nowrap">
                Relevance
              </span>
              <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full transition-all"
                  style={{ width: `${Math.round(doc.relevance_score * 100)}%` }}
                />
              </div>
              <span className="text-[10px] font-medium text-gray-700">
                {Math.round(doc.relevance_score * 100)}%
              </span>
            </div>

            {doc.last_updated && (
              <span className="text-[10px] text-gray-400 whitespace-nowrap">
                Updated {doc.last_updated}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
