import { useState } from "react";
import type { AnalysisResult } from "../types";
import SummaryPanel from "./SummaryPanel";
import TranscriptPanel from "./TranscriptPanel";
import KeyMomentsPanel from "./KeyMomentsPanel";
import QueryPanel from "./QueryPanel";

type Tab = "summary" | "moments" | "transcript" | "query";

interface Props {
  analysis: AnalysisResult;
  onReset: () => void;
}

function fmtDuration(secs: number) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}m ${s}s`;
}

export default function AnalysisView({ analysis, onReset }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>("summary");

  const tabs: { id: Tab; label: string; count?: number }[] = [
    { id: "summary", label: "Evidence Summary" },
    { id: "moments", label: "Key Moments", count: analysis.key_moments.length },
    { id: "transcript", label: "Transcript", count: analysis.transcript.length },
    { id: "query", label: "Ask a Question" },
  ];

  const highMoments = analysis.key_moments.filter((m) => m.significance === "high").length;
  const miranda = analysis.summary?.miranda_rights_read;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Case header */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-0.5 rounded-full">
                Analysis Complete
              </span>
              <span className="text-xs text-gray-400">via Azure Video Indexer + GPT-4o</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">{analysis.case_number}</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Video duration: {fmtDuration(analysis.video_duration_seconds ?? 0)} &nbsp;·&nbsp;
              {analysis.speakers.length} speakers identified
            </p>
          </div>

          <div className="flex gap-3 flex-wrap">
            {/* Miranda badge */}
            <div className={`px-3 py-2 rounded-xl text-xs font-semibold border ${
              miranda === true
                ? "bg-yellow-50 text-yellow-800 border-yellow-200"
                : miranda === false
                ? "bg-red-50 text-red-800 border-red-200"
                : "bg-gray-50 text-gray-600 border-gray-200"
            }`}>
              {miranda === true
                ? `Miranda Read @ ${analysis.summary?.miranda_timestamp}`
                : miranda === false
                ? "⚠ Miranda NOT Read Pre-Arrest"
                : "Miranda: Unknown"}
            </div>

            {/* Force badge */}
            <div className={`px-3 py-2 rounded-xl text-xs font-semibold border ${
              analysis.summary?.use_of_force_detected
                ? "bg-red-50 text-red-800 border-red-200"
                : "bg-green-50 text-green-800 border-green-200"
            }`}>
              {analysis.summary?.use_of_force_detected ? "Force Detected" : "No Force Detected"}
            </div>

            {/* High significance moments */}
            {highMoments > 0 && (
              <div className="px-3 py-2 rounded-xl text-xs font-semibold border bg-orange-50 text-orange-800 border-orange-200">
                {highMoments} High-Priority Moments
              </div>
            )}

            <button
              onClick={onReset}
              className="px-3 py-2 rounded-xl text-xs font-semibold border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors"
            >
              New Analysis
            </button>
          </div>
        </div>

        {/* Speaker breakdown */}
        <div className="mt-4 flex gap-3 flex-wrap">
          {analysis.speakers.map((s) => (
            <div key={s.id} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5 text-xs">
              <span className={`w-2 h-2 rounded-full ${
                s.role === "officer" ? "bg-blue-500" :
                s.role === "suspect" ? "bg-orange-500" :
                "bg-gray-400"
              }`}></span>
              <span className="font-medium">{s.label}</span>
              <span className="text-gray-400">{fmtDuration(s.total_speech_seconds)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-gray-100 rounded-xl p-1">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
              activeTab === t.id
                ? "bg-white text-[#003366] shadow-sm"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            {t.label}
            {t.count !== undefined && (
              <span className="ml-1 text-xs bg-gray-200 text-gray-600 rounded-full px-1.5 py-0.5">
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "summary" && <SummaryPanel summary={analysis.summary!} />}
      {activeTab === "moments" && <KeyMomentsPanel moments={analysis.key_moments} />}
      {activeTab === "transcript" && <TranscriptPanel lines={analysis.transcript} />}
      {activeTab === "query" && <QueryPanel jobId={analysis.job_id} />}
    </div>
  );
}
