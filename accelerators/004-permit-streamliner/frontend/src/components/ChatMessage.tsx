import type { ChatMessage as ChatMessageType } from "../types";

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-navy-700 text-white rounded-br-md"
            : "bg-white text-gray-900 border border-gray-200 rounded-bl-md shadow-sm"
        }`}
        style={isUser ? { backgroundColor: "#1B2A4A" } : {}}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>

        {message.confidence !== undefined && !isUser && (
          <div className="mt-2 flex items-center gap-2">
            <div className="h-1.5 flex-1 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${message.confidence * 100}%`,
                  backgroundColor:
                    message.confidence > 0.8
                      ? "#D4A537"
                      : message.confidence > 0.5
                      ? "#F59E0B"
                      : "#EF4444",
                }}
              />
            </div>
            <span className="text-[10px] text-gray-400">
              {Math.round(message.confidence * 100)}%
            </span>
          </div>
        )}

        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wide mb-1">
              References
            </p>
            {message.citations.map((c, i) => (
              <p key={i} className="text-[11px] text-gray-500">
                📋 {c.source}
                {c.policy_ref && ` (${c.policy_ref})`}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
