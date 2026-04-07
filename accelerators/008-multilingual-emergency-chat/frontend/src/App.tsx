import { useRef, useEffect, useState } from "react";
import { useChat } from "./hooks/useChat";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import AirQualityBadge from "./components/AirQualityBadge";
import AlertCards from "./components/AlertCards";
import ShelterList from "./components/ShelterList";
import Footer from "./components/Footer";

export default function App() {
  const { messages, loading, error, sendMessage } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [zip, setZip] = useState("");
  const [activeZip, setActiveZip] = useState<string | undefined>();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const applyZip = () => {
    const trimmed = zip.trim();
    setActiveZip(trimmed || undefined);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-orange-700 to-red-700 text-white px-4 py-3 shadow-md">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <span className="text-2xl">🚨</span>
          <div className="flex-1">
            <h1 className="text-lg font-bold leading-tight">
              Cal OES Emergency Chatbot
            </h1>
            <p className="text-xs text-orange-200">
              Multilingual emergency information for California
            </p>
          </div>
          <button
            type="button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden bg-orange-800 hover:bg-orange-900 text-white rounded px-3 py-1.5 text-sm"
            data-testid="sidebar-toggle"
          >
            {sidebarOpen ? "✕ Close" : "📊 Info"}
          </button>
        </div>
      </header>

      {/* Zip + AQI bar */}
      <div className="bg-gray-900 border-b border-gray-800 px-4 py-2">
        <div className="max-w-5xl mx-auto flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <label htmlFor="zip-field" className="text-xs text-gray-400 whitespace-nowrap">
              📍 ZIP Code
            </label>
            <input
              id="zip-field"
              type="text"
              value={zip}
              onChange={(e) => setZip(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && applyZip()}
              placeholder="e.g. 95814"
              maxLength={10}
              className="bg-gray-800 text-gray-100 rounded px-2 py-1 text-sm border border-gray-600 w-24 placeholder-gray-500"
              data-testid="zip-input"
            />
            <button
              type="button"
              onClick={applyZip}
              className="bg-orange-600 hover:bg-orange-700 text-white rounded px-3 py-1 text-xs font-medium"
              data-testid="zip-apply"
            >
              Go
            </button>
          </div>
          <div className="flex-1 min-w-0">
            <AirQualityBadge zip={activeZip} />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto" data-testid="chat-messages">
            <div className="max-w-3xl mx-auto px-4 py-4">
              {messages.length === 0 && (
                <div className="text-center text-gray-400 mt-12">
                  <p className="text-4xl mb-4">🆘</p>
                  <p className="text-sm">
                    Ask about active alerts, evacuations, shelters, or air quality.
                  </p>
                  <p className="text-xs text-gray-300 mt-1">
                    For life-threatening emergencies, call 911.
                  </p>
                </div>
              )}
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              {loading && (
                <div className="flex justify-start mb-3">
                  <div className="bg-gray-100 rounded-xl px-4 py-3 text-sm text-gray-500 animate-pulse">
                    Searching emergency data…
                  </div>
                </div>
              )}
              {error && (
                <div className="text-center text-red-500 text-sm py-2">
                  Error: {error}
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </div>

          {/* Input */}
          <div className="max-w-3xl mx-auto w-full">
            <ChatInput onSend={sendMessage} disabled={loading} />
          </div>
        </main>

        {/* Sidebar — alerts & shelters */}
        <aside
          className={`${
            sidebarOpen ? "block" : "hidden"
          } lg:block w-full lg:w-80 bg-gray-900 border-l border-gray-800 overflow-y-auto p-3 space-y-4`}
          data-testid="info-sidebar"
        >
          <div>
            <h2 className="text-sm font-bold text-orange-400 uppercase tracking-wide mb-2">
              ⚠️ Active Alerts
            </h2>
            <AlertCards zip={activeZip} />
          </div>
          <div>
            <h2 className="text-sm font-bold text-orange-400 uppercase tracking-wide mb-2">
              🏠 Nearby Shelters
            </h2>
            <ShelterList zip={activeZip} />
          </div>
        </aside>
      </div>
      <Footer />
    </div>
  );
}
