import type { ChatMessage as ChatMessageType } from "../types";

interface Props {
  message: ChatMessageType;
}

const SEVERITY_COLORS: Record<string, string> = {
  extreme: "bg-red-700 text-white",
  severe: "bg-orange-600 text-white",
  moderate: "bg-yellow-500 text-gray-900",
  minor: "bg-blue-400 text-white",
};

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 ${
          isUser
            ? "bg-orange-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-800 rounded-bl-sm"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>

        {/* Alert cards */}
        {message.data?.alerts && message.data.alerts.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.data.alerts.map((alert) => (
              <div
                key={alert.alert_id}
                className={`rounded-lg p-3 ${SEVERITY_COLORS[alert.severity] || "bg-gray-200"}`}
              >
                <p className="font-bold text-xs uppercase">{alert.severity}</p>
                <p className="font-semibold text-sm">{alert.title}</p>
                <p className="text-xs mt-1">{alert.description}</p>
                {alert.instructions && (
                  <p className="text-xs mt-1 italic">{alert.instructions}</p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Shelter cards */}
        {message.data?.shelters && message.data.shelters.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.data.shelters.map((s) => (
              <div key={s.shelter_id} className="bg-white text-gray-800 rounded-lg p-3 border">
                <p className="font-semibold text-sm">{s.name}</p>
                <p className="text-xs text-gray-500">
                  {s.address}, {s.city} · {s.status}
                </p>
                <p className="text-xs">
                  Capacity: {s.current_occupancy}/{s.capacity}
                  {s.accepts_pets && " 🐾"} {s.ada_accessible && " ♿"}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Citations */}
        {message.data?.citations && message.data.citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {message.data.citations.map((c, i) => (
              <span
                key={i}
                className="text-[10px] bg-gray-200 text-gray-600 rounded px-1.5 py-0.5"
              >
                {c.source}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
