import type { ChatMessage as ChatMessageType } from "../types";

interface Props {
  message: ChatMessageType;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 border-green-200",
  pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
  denied: "bg-red-100 text-red-800 border-red-200",
  exhausted: "bg-gray-100 text-gray-800 border-gray-200",
  on_hold: "bg-orange-100 text-orange-800 border-orange-200",
};

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-white text-gray-900 border border-gray-200 rounded-bl-md shadow-sm"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>

        {message.claim_status && (
          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold text-sm text-blue-900">
                {message.claim_status.claim_type} Claim
              </span>
              <span
                className={`text-xs px-2 py-0.5 rounded-full border ${
                  STATUS_COLORS[message.claim_status.status] ||
                  "bg-gray-100 text-gray-800"
                }`}
              >
                {message.claim_status.status}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-700">
              <div>
                <span className="text-gray-500">ID:</span>{" "}
                {message.claim_status.claim_id}
              </div>
              <div>
                <span className="text-gray-500">Weekly:</span> $
                {message.claim_status.weekly_benefit_amount.toFixed(2)}
              </div>
              <div>
                <span className="text-gray-500">Balance:</span> $
                {message.claim_status.remaining_balance.toFixed(2)}
              </div>
              {message.claim_status.next_payment_date && (
                <div>
                  <span className="text-gray-500">Next payment:</span>{" "}
                  {new Date(
                    message.claim_status.next_payment_date
                  ).toLocaleDateString()}
                </div>
              )}
            </div>
            {message.claim_status.pending_issues.length > 0 && (
              <div className="mt-2 text-xs">
                <span className="text-red-600 font-medium">
                  Pending issues:
                </span>
                <ul className="mt-1 space-y-0.5">
                  {message.claim_status.pending_issues.map((issue, i) => (
                    <li key={i} className="text-red-600">
                      ⚠ {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

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
                {message.eligibility.claim_type} Eligibility
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

        {message.document_checklist && message.document_checklist.length > 0 && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="font-semibold text-sm text-amber-900 mb-2">
              Document Checklist
            </p>
            <div className="space-y-1">
              {message.document_checklist.map((doc, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span
                    className={`w-4 h-4 rounded border flex items-center justify-center ${
                      doc.submitted
                        ? "bg-green-500 border-green-600 text-white"
                        : "bg-white border-gray-300"
                    }`}
                  >
                    {doc.submitted && "✓"}
                  </span>
                  <span className="text-gray-800">
                    {doc.name}
                    {doc.required && (
                      <span className="text-red-500 ml-1">*</span>
                    )}
                  </span>
                </div>
              ))}
            </div>
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
