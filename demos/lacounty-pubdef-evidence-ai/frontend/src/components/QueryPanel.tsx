import { useState } from "react";
import { api } from "../api/client";
import type { EvidenceQueryResponse } from "../types";

interface Props {
  jobId: string;
}

const SUGGESTED_QUESTIONS = [
  "Were Miranda rights read before questioning began?",
  "Did the subject give clear consent to the vehicle search?",
  "Did the subject attempt to revoke consent?",
  "What reason did the officer give for the traffic stop?",
  "Was any force used during the arrest?",
  "What happened at the 10-minute mark?",
  "Did the subject clearly invoke their right to an attorney?",
];

const CONFIDENCE_STYLES = {
  high: "bg-green-50 text-green-800 border-green-200",
  medium: "bg-amber-50 text-amber-800 border-amber-200",
  low: "bg-red-50 text-red-800 border-red-200",
};

export default function QueryPanel({ jobId }: Props) {
  const [question, setQuestion] = useState("");
  const [responses, setResponses] = useState<EvidenceQueryResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAsk(q?: string) {
    const finalQ = (q ?? question).trim();
    if (!finalQ) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.queryEvidence({ job_id: jobId, question: finalQ });
      setResponses((prev) => [res, ...prev]);
      setQuestion("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Input */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <h3 className="text-base font-semibold text-gray-800 mb-1">Ask About the Evidence</h3>
        <p className="text-sm text-gray-500 mb-4">
          Ask natural-language questions about the body cam footage. GPT-4o answers using only the analyzed transcript.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && handleAsk()}
            placeholder="Were Miranda rights read before questioning began?"
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#003366]"
          />
          <button
            onClick={() => handleAsk()}
            disabled={loading || !question.trim()}
            className="bg-[#003366] text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-[#1a4d8f] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "..." : "Ask"}
          </button>
        </div>

        {error && <p className="text-xs text-red-600 mt-2">{error}</p>}

        {/* Suggested questions */}
        <div className="mt-4">
          <p className="text-xs text-gray-400 mb-2 font-medium">SUGGESTED QUESTIONS</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => handleAsk(q)}
                disabled={loading}
                className="text-xs border border-[#003366] text-[#003366] rounded-full px-3 py-1 hover:bg-blue-50 transition-colors disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Responses */}
      {responses.map((res, i) => (
        <div key={i} className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-start gap-3 mb-3">
            <div className="w-7 h-7 rounded-full bg-[#c9a84c] flex items-center justify-center flex-shrink-0">
              <span className="text-[#003366] text-xs font-bold">Q</span>
            </div>
            <p className="text-sm font-medium text-gray-800 pt-1">{res.question}</p>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-[#003366] flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-bold">A</span>
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-700 leading-relaxed">{res.answer}</p>

              {res.supporting_timestamps.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-xs text-gray-400">Supporting timestamps:</span>
                  {res.supporting_timestamps.map((ts) => (
                    <span
                      key={ts}
                      className="font-mono text-xs bg-[#003366] text-white px-2 py-0.5 rounded-full"
                    >
                      {ts}
                    </span>
                  ))}
                </div>
              )}

              <div className="mt-3">
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                    CONFIDENCE_STYLES[res.confidence]
                  }`}
                >
                  {res.confidence.charAt(0).toUpperCase() + res.confidence.slice(1)} Confidence
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}

      {responses.length === 0 && (
        <div className="text-center py-12 text-gray-400 text-sm">
          Ask a question above to get started. Results are grounded only in the analyzed transcript.
        </div>
      )}
    </div>
  );
}
