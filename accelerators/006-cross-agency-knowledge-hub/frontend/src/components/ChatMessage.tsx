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
            ? "bg-blue-800 text-white rounded-br-md"
            : "bg-white text-gray-900 border border-gray-200 rounded-bl-md shadow-sm"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>

        {message.documents && message.documents.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.documents.map((doc) => (
              <div
                key={doc.doc_id}
                className="p-3 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold bg-blue-900 text-white px-2 py-0.5 rounded">
                    {doc.agency}
                  </span>
                  <span className="text-xs text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                    {doc.document_type}
                  </span>
                  <span className="text-xs text-gray-400">
                    {Math.round(doc.relevance_score * 100)}% match
                  </span>
                </div>
                <p className="font-semibold text-sm text-blue-900">
                  {doc.title}
                </p>
                <p className="text-xs text-gray-600 mt-1">{doc.summary}</p>
              </div>
            ))}
          </div>
        )}

        {message.experts && message.experts.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.experts.map((exp) => (
              <div
                key={exp.expert_id}
                className="p-3 bg-amber-50 border border-amber-200 rounded-lg"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      exp.available ? "bg-green-500" : "bg-gray-400"
                    }`}
                  />
                  <span className="font-semibold text-sm text-gray-900">
                    {exp.name}
                  </span>
                  <span className="text-xs text-gray-500">
                    {exp.agency} — {exp.department}
                  </span>
                </div>
                <p className="text-xs text-gray-600">
                  {exp.expertise_areas.join(", ")}
                </p>
              </div>
            ))}
          </div>
        )}

        {message.cross_references && message.cross_references.length > 0 && (
          <div className="mt-3 space-y-1">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Cross-References
            </p>
            {message.cross_references.map((ref, i) => (
              <div
                key={i}
                className="text-xs text-gray-600 p-2 bg-gray-50 border border-gray-200 rounded"
              >
                <span className="font-medium">{ref.source_doc_id}</span>
                {" → "}
                <span className="font-medium">{ref.target_doc_id}</span>
                <span className="text-amber-700 ml-1">({ref.relationship})</span>
                <p className="mt-0.5">{ref.description}</p>
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
                {c.agency && ` (${c.agency})`}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
