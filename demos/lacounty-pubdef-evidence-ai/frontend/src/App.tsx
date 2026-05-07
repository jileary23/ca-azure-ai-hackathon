import { useState } from "react";
import { api } from "./api/client";
import SubmitPanel from "./components/SubmitPanel";
import AnalysisView from "./components/AnalysisView";
import type { AnalysisResult } from "./types";

type AppState = "idle" | "loading" | "done" | "error";

export default function App() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleSubmit(caseNumber: string, description: string) {
    setAppState("loading");
    setErrorMsg("");
    try {
      const res = await api.submitVideo({
        case_number: caseNumber,
        description,
        use_mock: true,
      });
      const result = await api.getAnalysis(res.job_id);
      setAnalysis(result);
      setAppState("done");
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Unknown error");
      setAppState("error");
    }
  }

  function handleReset() {
    setAnalysis(null);
    setAppState("idle");
    setErrorMsg("");
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-[#003366] text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-[#c9a84c] rounded-full flex items-center justify-center">
              <span className="text-[#003366] font-bold text-lg">LA</span>
            </div>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              LA County Public Defender
            </h1>
            <p className="text-blue-200 text-sm">
              Evidence AI — Body Cam Analysis powered by Azure Video Indexer &amp; GPT-4o
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2 text-xs text-blue-300">
            <span className="inline-block w-2 h-2 rounded-full bg-green-400"></span>
            Mock Mode — No evidence leaves this browser
          </div>
        </div>
      </header>

      {/* Security banner */}
      <div className="bg-amber-50 border-b border-amber-200">
        <div className="max-w-6xl mx-auto px-6 py-2 text-xs text-amber-800 flex items-center gap-2">
          <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
          </svg>
          <span>
            <strong>Demo Environment.</strong> In production, all evidence processing occurs within your LA County Azure Government tenant. Data is never sent to third-party services. CJIS compliant.
          </span>
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        {appState === "idle" && (
          <SubmitPanel onSubmit={handleSubmit} />
        )}

        {appState === "loading" && (
          <div className="flex flex-col items-center justify-center py-24 gap-6">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 rounded-full border-4 border-blue-100"></div>
              <div className="absolute inset-0 rounded-full border-4 border-[#003366] border-t-transparent animate-spin"></div>
            </div>
            <div className="text-center">
              <p className="text-lg font-semibold text-gray-800">Analyzing evidence...</p>
              <p className="text-sm text-gray-500 mt-1">
                Azure Video Indexer is processing the footage and GPT-4o is generating the legal summary.
              </p>
            </div>
            <div className="flex flex-col gap-2 text-sm text-gray-500 bg-white rounded-lg border p-4 w-full max-w-md">
              {[
                "Extracting transcript with speaker diarization",
                "Identifying key moments and scene changes",
                "Detecting named entities and legal events",
                "Generating GPT-4o evidence summary",
                "Flagging defense considerations",
              ].map((step, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-[#003366] border-t-transparent animate-spin flex-shrink-0"></div>
                  {step}
                </div>
              ))}
            </div>
          </div>
        )}

        {appState === "error" && (
          <div className="text-center py-24">
            <div className="text-red-500 text-5xl mb-4">⚠</div>
            <p className="text-xl font-semibold text-gray-800 mb-2">Analysis failed</p>
            <p className="text-gray-500 mb-6">{errorMsg}</p>
            <button
              onClick={handleReset}
              className="bg-[#003366] text-white px-6 py-2 rounded-lg hover:bg-[#1a4d8f] transition-colors"
            >
              Try again
            </button>
          </div>
        )}

        {appState === "done" && analysis && (
          <AnalysisView analysis={analysis} onReset={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-[#003366] text-blue-300 text-xs py-3 px-6 text-center mt-auto">
        LA County Public Defender — Evidence AI Demo &nbsp;|&nbsp; Powered by Microsoft Azure Video Indexer + Azure OpenAI GPT-4o &nbsp;|&nbsp; CJIS Compliant Architecture
      </footer>
    </div>
  );
}
