import { useRef, useEffect, useState } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import EligibilityForm from "./components/EligibilityForm";
import EligibilityResults from "./components/EligibilityResults";
import type { EligibilityResult } from "./types";

type Tab = "chat" | "screening";

export default function App() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [screeningResults, setScreeningResults] = useState<EligibilityResult[]>(
    []
  );

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50 flex flex-col">
      {/* Header */}
      <header className="bg-blue-900 text-white px-6 py-4 shadow-lg">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-yellow-400 rounded-full flex items-center justify-center text-blue-900 font-bold text-lg">
            BC
          </div>
          <div>
            <h1 className="text-xl font-bold">BenefitsCal Navigator</h1>
            <p className="text-blue-200 text-xs">
              AI-powered benefits eligibility assistant for California
            </p>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-3xl w-full mx-auto px-4 pt-4">
        <div className="flex gap-2" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === "chat"}
            onClick={() => setActiveTab("chat")}
            className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
              activeTab === "chat"
                ? "bg-white text-blue-900 border border-b-0 border-gray-200"
                : "bg-gray-100 text-gray-600 hover:text-blue-900"
            }`}
          >
            💬 Chat
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "screening"}
            onClick={() => setActiveTab("screening")}
            className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
              activeTab === "screening"
                ? "bg-white text-blue-900 border border-b-0 border-gray-200"
                : "bg-gray-100 text-gray-600 hover:text-blue-900"
            }`}
          >
            📋 Eligibility Screening
          </button>
        </div>
      </div>

      {/* Chat tab */}
      {activeTab === "chat" && (
        <>
          <main
            data-testid="chat-messages"
            className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 overflow-y-auto"
          >
            {messages.length === 0 && (
              <div className="text-center py-16">
                <h2 className="text-2xl font-bold text-blue-900 mb-2">
                  Welcome to BenefitsCal Navigator
                </h2>
                <p className="text-gray-600 mb-6">
                  Ask about CalFresh, CalWORKs, General Relief, CAPI, and more.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                  {[
                    "Am I eligible for CalFresh?",
                    "How do I apply for CalWORKs?",
                    "What documents do I need?",
                    "Where is the nearest office?",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition text-sm text-gray-700"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <ChatMessage key={msg.id} message={msg} index={idx} />
            ))}

            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-white rounded-2xl px-4 py-3 border border-gray-200 shadow-sm">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm mb-4">
                {error}
              </div>
            )}

            <div ref={bottomRef} />
          </main>

          <footer className="border-t border-gray-200 bg-white px-4 py-3">
            <div className="max-w-3xl mx-auto">
              <ChatInput onSend={sendMessage} disabled={isLoading} />
            </div>
          </footer>
        </>
      )}

      {/* Screening tab */}
      {activeTab === "screening" && (
        <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 space-y-6 overflow-y-auto">
          <EligibilityForm onResults={setScreeningResults} />
          <EligibilityResults results={screeningResults} />
        </main>
      )}
    </div>
  );
}
