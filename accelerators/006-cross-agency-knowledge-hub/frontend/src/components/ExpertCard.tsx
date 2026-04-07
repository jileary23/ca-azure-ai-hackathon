import type { ExpertInfo } from "../types";

interface Props {
  expert: ExpertInfo;
}

export default function ExpertCard({ expert }: Props) {
  return (
    <div
      data-testid="expert-card"
      className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition"
    >
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 bg-blue-900 text-amber-300 rounded-full flex items-center justify-center font-bold text-sm">
          {expert.name
            .split(" ")
            .map((n) => n[0])
            .join("")
            .slice(0, 2)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm text-gray-900 truncate">
              {expert.name}
            </span>
            <span
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                expert.available ? "bg-green-500" : "bg-gray-400"
              }`}
              title={expert.available ? "Available" : "Unavailable"}
            />
          </div>
          <p className="text-xs text-gray-500 truncate">
            {expert.agency} — {expert.department}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {expert.expertise_areas.map((area) => (
          <span
            key={area}
            className="text-[10px] font-medium bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full"
          >
            {area}
          </span>
        ))}
      </div>

      <a
        href={`mailto:${expert.email}`}
        className="text-xs text-blue-800 hover:text-blue-600 underline"
      >
        {expert.email}
      </a>
    </div>
  );
}
