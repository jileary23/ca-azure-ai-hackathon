import type { ChatMessage as ChatMessageType } from "../types";

interface Props {
  message: ChatMessageType;
  index?: number;
}

export default function ChatMessage({ message, index }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`} data-testid={index !== undefined ? `message-${index}` : undefined}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-700 text-white rounded-br-md"
            : "bg-white text-gray-900 border border-gray-200 rounded-bl-md shadow-sm"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>

        {message.eligibility && (
          <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`inline-block w-3 h-3 rounded-full ${
                  message.eligibility.likely_eligible
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              />
              <span className="font-semibold text-sm text-green-800">
                {message.eligibility.program}
              </span>
              <span className="text-xs text-gray-500">
                ({Math.round(message.eligibility.confidence * 100)}% confidence)
              </span>
            </div>
            {message.eligibility.next_steps.length > 0 && (
              <ul className="mt-2 text-xs text-gray-700 space-y-1">
                {message.eligibility.next_steps.map((step, i) => (
                  <li key={i}>→ {step}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {message.programs && message.programs.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.programs.map((prog) => (
              <div
                key={prog.program_id}
                className="p-2 bg-blue-50 border border-blue-100 rounded-lg"
              >
                <p className="font-semibold text-sm text-blue-900">
                  {prog.name}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {prog.description}
                </p>
              </div>
            ))}
          </div>
        )}

        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wide mb-1">
              Sources
            </p>
            {message.citations.map((c, i) => (
              <p key={i} className="text-[11px] text-gray-500">
                📄 {c.source}
                {c.policy_ref && ` (${c.policy_ref})`}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
