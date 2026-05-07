import type { EvidenceSummary } from "../types";

interface Props {
  summary: EvidenceSummary;
}

export default function SummaryPanel({ summary }: Props) {
  return (
    <div className="flex flex-col gap-5">
      {/* Narrative */}
      <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-base font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-[#003366] text-white text-xs flex items-center justify-center">1</span>
          Incident Narrative
        </h3>
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{summary.narrative}</p>
      </section>

      {/* Timeline */}
      <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-base font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-[#003366] text-white text-xs flex items-center justify-center">2</span>
          Chronological Timeline
        </h3>
        <ol className="relative border-l border-gray-200 ml-3 flex flex-col gap-4">
          {summary.timeline.map((item, i) => {
            const [time, ...rest] = item.split(" — ");
            return (
              <li key={i} className="ml-4">
                <span className="absolute -left-2 w-4 h-4 rounded-full bg-[#003366] border-2 border-white flex items-center justify-center mt-0.5">
                </span>
                <p className="text-sm text-gray-700">
                  <span className="font-mono font-semibold text-[#003366] text-xs">{time}</span>
                  {rest.length > 0 && <span> — {rest.join(" — ")}</span>}
                </p>
              </li>
            );
          })}
        </ol>
      </section>

      {/* Discrepancies */}
      {summary.discrepancies.length > 0 && (
        <section className="bg-amber-50 rounded-2xl border border-amber-200 shadow-sm p-6">
          <h3 className="text-base font-semibold text-amber-900 mb-3 flex items-center gap-2">
            <span>⚠</span> Potential Discrepancies &amp; Inconsistencies
          </h3>
          <ul className="flex flex-col gap-3">
            {summary.discrepancies.map((d, i) => (
              <li key={i} className="flex gap-3 text-sm text-amber-900">
                <span className="flex-shrink-0 font-bold">{i + 1}.</span>
                <span>{d}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Defense considerations */}
      {summary.defense_considerations.length > 0 && (
        <section className="bg-red-50 rounded-2xl border border-red-200 shadow-sm p-6">
          <h3 className="text-base font-semibold text-red-900 mb-3 flex items-center gap-2">
            <span>⚖</span> Defense Considerations
            <span className="text-xs font-normal text-red-600 ml-auto">Attorney-client privileged</span>
          </h3>
          <ul className="flex flex-col gap-4">
            {summary.defense_considerations.map((item, i) => {
              const colonIdx = item.indexOf(":");
              const label = colonIdx > -1 ? item.slice(0, colonIdx) : null;
              const body = colonIdx > -1 ? item.slice(colonIdx + 1).trim() : item;
              return (
                <li key={i} className="text-sm text-red-900 flex gap-3">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-red-200 text-red-800 text-xs font-bold flex items-center justify-center mt-0.5">{i + 1}</span>
                  <div>
                    {label && <span className="font-semibold">{label}: </span>}
                    <span>{body}</span>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      )}
    </div>
  );
}
