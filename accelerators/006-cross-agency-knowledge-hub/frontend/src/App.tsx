import { useRef, useEffect, useState } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import SearchBar from "./components/SearchBar";
import SearchResults from "./components/SearchResults";
import ExpertCard from "./components/ExpertCard";
import { getExperts } from "./api/apiClient";
import type { DocumentResult, ExpertInfo } from "./types";

type TabId = "chat" | "search" | "experts";

export default function App() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  const [activeTab, setActiveTab] = useState<TabId>("chat");

  // Search tab state
  const [searchResults, setSearchResults] = useState<DocumentResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Experts tab state
  const [expertTopic, setExpertTopic] = useState("");
  const [experts, setExperts] = useState<ExpertInfo[]>([]);
  const [expertLoading, setExpertLoading] = useState(false);
  const [expertError, setExpertError] = useState<string | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleExpertSearch = async () => {
    const trimmed = expertTopic.trim();
    if (!trimmed) return;
    setExpertLoading(true);
    setExpertError(null);
    try {
      const data = await getExperts(trimmed);
      setExperts(data);
    } catch (err) {
      setExpertError(err instanceof Error ? err.message : "Failed to load experts");
      setExperts([]);
    } finally {
      setExpertLoading(false);
    }
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: "chat", label: "Chat" },
    { id: "search", label: "Search" },
    { id: "experts", label: "Experts" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-blue-50 flex flex-col">
      {/* Header */}
      <header className="bg-blue-900 text-white px-6 py-4 shadow-lg">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-400 rounded-full flex items-center justify-center text-blue-900 font-bold text-lg">
            KH
          </div>
          <div>
            <h1 className="text-xl font-bold">Cross-Agency Knowledge Hub</h1>
            <p className="text-blue-200 text-xs">
              Federated search across California state government knowledge
              bases
            </p>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              data-testid={`tab-${tab.id}`}
              className={`px-5 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? "border-amber-500 text-blue-900"
                  : "border-transparent text-gray-500 hover:text-blue-900 hover:border-gray-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main content */}
      <main
        data-testid="chat-messages"
        className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 overflow-y-auto"
      >
        {/* ---- Chat Tab ---- */}
        {activeTab === "chat" && (
          <>
            {messages.length === 0 && (
              <div className="text-center py-16">
                <h2 className="text-2xl font-bold text-blue-900 mb-2">
                  Welcome to the Knowledge Hub
                </h2>
                <p className="text-gray-600 mb-6">
                  Search policies, find experts, and discover cross-references
                  across California state agencies.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                  {[
                    "Find CDSS policy on CalFresh",
                    "Who is the expert on procurement?",
                    "Search across agencies for data governance",
                    "What agencies are available?",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 hover:border-amber-400 hover:shadow-md transition text-sm text-gray-700"
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
                    <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                    <span className="w-2 h-2 bg-amber-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm mb-4">
                {error}
              </div>
            )}
          </>
        )}

        {/* ---- Search Tab ---- */}
        {activeTab === "search" && (
          <div className="space-y-4">
            <SearchBar
              onResults={setSearchResults}
              onLoading={setSearchLoading}
              onError={setSearchError}
            />
            {searchLoading && (
              <p className="text-sm text-gray-500 animate-pulse">
                Searching...
              </p>
            )}
            {searchError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                {searchError}
              </div>
            )}
            <SearchResults results={searchResults} />
            {!searchLoading &&
              searchResults.length === 0 &&
              !searchError && (
                <p className="text-center text-gray-400 text-sm py-12">
                  Search for documents across California state agencies
                </p>
              )}
          </div>
        )}

        {/* ---- Experts Tab ---- */}
        {activeTab === "experts" && (
          <div className="space-y-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleExpertSearch();
              }}
              className="flex gap-2"
              data-testid="expert-search"
            >
              <input
                type="text"
                value={expertTopic}
                onChange={(e) => setExpertTopic(e.target.value)}
                placeholder="Enter a topic to find experts..."
                data-testid="expert-topic-input"
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                aria-label="Expert topic"
              />
              <button
                type="submit"
                disabled={!expertTopic.trim() || expertLoading}
                data-testid="expert-search-submit"
                className="bg-amber-500 hover:bg-amber-600 text-white rounded-lg px-5 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {expertLoading ? "..." : "Find Experts"}
              </button>
            </form>
            {expertLoading && (
              <p className="text-sm text-gray-500 animate-pulse">
                Finding experts...
              </p>
            )}
            {expertError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                {expertError}
              </div>
            )}
            {experts.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {experts.map((exp) => (
                  <ExpertCard key={exp.expert_id} expert={exp} />
                ))}
              </div>
            )}
            {!expertLoading && experts.length === 0 && !expertError && (
              <p className="text-center text-gray-400 text-sm py-12">
                Enter a topic to discover subject-matter experts across agencies
              </p>
            )}
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* Input (Chat tab only) */}
      {activeTab === "chat" && (
        <footer className="border-t border-gray-200 bg-white px-4 py-3">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </div>
        </footer>
      )}
    </div>
  );
}

