import { useRef, useEffect, useState } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import ClaimStatusForm from "./components/ClaimStatusForm";
import BenefitCalculator from "./components/BenefitCalculator";
import TimelineDisplay from "./components/TimelineDisplay";
import Footer from "./components/Footer";

type Tab = "chat" | "status" | "calculator";

const TABS: { id: Tab; label: string }[] = [
  { id: "chat", label: "Chat" },
  { id: "status", label: "Claim Status" },
  { id: "calculator", label: "Calculator" },
];

export default function App() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<Tab>("chat");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      {/* Header */}
      <header className="bg-blue-600 text-white px-6 py-4 shadow-lg">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-blue-600 font-bold text-lg">
            EDD
          </div>
          <div>
            <h1 className="text-xl font-bold">EDD Claims Assistant</h1>
            <p className="text-blue-100 text-xs">
              Unemployment Insurance · Disability Insurance · Paid Family Leave
            </p>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto flex">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
              data-testid={`tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Chat Tab */}
      {activeTab === "chat" && (
        <>
          <main
            className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 overflow-y-auto"
            data-testid="chat-messages"
          >
            {messages.length === 0 && (
              <div className="text-center py-16">
                <h2 className="text-2xl font-bold text-blue-900 mb-2">
                  Welcome to the EDD Claims Assistant
                </h2>
                <p className="text-gray-600 mb-6">
                  Get help with Unemployment Insurance, Disability Insurance, and
                  Paid Family Leave claims.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                  {[
                    "Check my unemployment claim status",
                    "Am I eligible for disability insurance?",
                    "How do I file a new UI claim?",
                    "What documents do I need?",
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

            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
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

      {/* Claim Status Tab */}
      {activeTab === "status" && (
        <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 space-y-6">
          <ClaimStatusForm />
          <TimelineDisplay claimType="ui" />
        </main>
      )}

      {/* Calculator Tab */}
      {activeTab === "calculator" && (
        <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6">
          <BenefitCalculator />
        </main>
      )}
      <Footer />
    </div>
  );
}

