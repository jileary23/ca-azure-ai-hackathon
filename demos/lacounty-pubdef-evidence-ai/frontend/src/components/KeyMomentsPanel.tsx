import type { KeyMoment } from "../types";

interface Props {
  moments: KeyMoment[];
}

const CATEGORY_STYLES: Record<string, { label: string; bg: string; text: string; border: string }> = {
  miranda: { label: "Miranda", bg: "bg-purple-50", text: "text-purple-800", border: "border-purple-200" },
  consent: { label: "Consent", bg: "bg-orange-50", text: "text-orange-800", border: "border-orange-200" },
  use_of_force: { label: "Use of Force", bg: "bg-red-50", text: "text-red-800", border: "border-red-200" },
  statement: { label: "Statement", bg: "bg-blue-50", text: "text-blue-800", border: "border-blue-200" },
  scene: { label: "Scene", bg: "bg-gray-50", text: "text-gray-700", border: "border-gray-200" },
};

const SIGNIFICANCE_DOT: Record<string, string> = {
  high: "bg-red-500",
  medium: "bg-amber-400",
  low: "bg-gray-300",
};

export default function KeyMomentsPanel({ moments }: Props) {
  const sorted = [...moments].sort((a, b) => a.timestamp_seconds - b.timestamp_seconds);

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <p className="text-sm text-gray-500">
          Automatically identified by Azure Video Indexer. High-significance moments are flagged for immediate attorney review.
        </p>
      </div>

      <div className="divide-y divide-gray-100">
        {sorted.map((moment, i) => {
          const style = CATEGORY_STYLES[moment.category] ?? CATEGORY_STYLES.scene;
          return (
            <div key={i} className={`px-6 py-4 flex gap-4 items-start ${moment.significance === "high" ? "bg-red-50/30" : ""}`}>
              {/* Timestamp */}
              <div className="flex-shrink-0 w-14 text-center">
                <span className="font-mono text-sm font-bold text-[#003366]">
                  {moment.timestamp_label}
                </span>
              </div>

              {/* Significance dot */}
              <div className="flex-shrink-0 pt-1.5">
                <span className={`block w-3 h-3 rounded-full ${SIGNIFICANCE_DOT[moment.significance]}`}></span>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${style.bg} ${style.text} ${style.border}`}>
                    {style.label}
                  </span>
                  {moment.significance === "high" && (
                    <span className="text-xs text-red-600 font-semibold">HIGH PRIORITY</span>
                  )}
                </div>
                <p className="text-sm text-gray-800">{moment.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
