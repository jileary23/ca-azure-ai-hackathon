import { useState } from "react";

interface Props {
  onSubmit: (caseNumber: string, description: string) => void;
}

const DEMO_CASES = [
  {
    caseNumber: "LA-2024-CR-087421",
    description:
      "Traffic stop on Crenshaw Blvd, March 12 2024. Client denies ownership of item found during search. Issues: consent validity, pre-arrest questioning without Miranda, attempted consent withdrawal.",
  },
];

export default function SubmitPanel({ onSubmit }: Props) {
  const [caseNumber, setCaseNumber] = useState("");
  const [description, setDescription] = useState("");

  function loadDemo() {
    setCaseNumber(DEMO_CASES[0].caseNumber);
    setDescription(DEMO_CASES[0].description);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (caseNumber.trim()) {
      onSubmit(caseNumber.trim(), description.trim());
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Hero */}
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-gray-900 mb-3">
          Body Cam Evidence Analysis
        </h2>
        <p className="text-gray-600 max-w-xl mx-auto">
          Submit a body cam video for automatic transcription, speaker diarization, 
          key moment extraction, and AI-generated defense summary — powered by 
          Azure Video Indexer and GPT-4o, running entirely within your county's 
          secure Azure environment.
        </p>
      </div>

      {/* Capability cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { icon: "🎙", label: "Speaker Diarization", desc: "Separates officer vs. subject voice" },
          { icon: "📋", label: "Auto Transcript", desc: "Full timestamped transcript" },
          { icon: "⚠️", label: "Key Moments", desc: "Miranda, consent, force flags" },
          { icon: "⚖️", label: "Defense Brief", desc: "GPT-4o legal considerations" },
        ].map((c) => (
          <div key={c.label} className="bg-white rounded-xl border border-gray-200 p-4 text-center shadow-sm">
            <div className="text-3xl mb-2">{c.icon}</div>
            <div className="font-semibold text-sm text-gray-800">{c.label}</div>
            <div className="text-xs text-gray-500 mt-1">{c.desc}</div>
          </div>
        ))}
      </div>

      {/* Form */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-800">Submit Evidence for Analysis</h3>
          <button
            type="button"
            onClick={loadDemo}
            className="text-sm text-[#003366] border border-[#003366] rounded-lg px-3 py-1 hover:bg-blue-50 transition-colors"
          >
            Load Demo Case
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Case Number <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              placeholder="LA-2024-CR-087421"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#003366] focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Attorney Notes / Context{" "}
              <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe key issues to watch for (e.g., consent, Miranda timing, use of force)"
              rows={4}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#003366] focus:border-transparent resize-none"
            />
          </div>

          <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800 border border-blue-100">
            <strong>Demo Mode:</strong> This demo uses a pre-processed body cam scenario (Incident 03-12-2024, 
            case LA-2024-CR-087421). In production, you would upload a video file or provide an Azure Blob Storage URL.
          </div>

          <button
            type="submit"
            className="bg-[#003366] text-white font-semibold py-3 rounded-xl hover:bg-[#1a4d8f] transition-colors text-sm"
          >
            Analyze Evidence →
          </button>
        </form>
      </div>
    </div>
  );
}
