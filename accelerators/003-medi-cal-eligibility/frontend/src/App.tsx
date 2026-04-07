import { useEffect, useState, useRef } from "react";
import { getHealth } from "./api/apiClient";
import { useChat } from "./hooks/useChat";
import type { HealthStatus } from "./types";
import EligibilityScreener from "./components/EligibilityScreener";
import DocumentUpload from "./components/DocumentUpload";
import ProgramList from "./components/ProgramList";
import Footer from "./components/Footer";

type Tab = "chat" | "screening" | "programs";

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [input, setInput] = useState("");
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  const tabStyle = (tab: Tab): React.CSSProperties => ({
    padding: "10px 20px",
    border: "none",
    borderBottom: activeTab === tab ? "3px solid #1a56db" : "3px solid transparent",
    background: "none",
    color: activeTab === tab ? "#1a56db" : "#666",
    fontWeight: activeTab === tab ? 700 : 400,
    fontSize: 14,
    cursor: "pointer",
  });

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f0f7ff", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{ background: "linear-gradient(135deg, #1a56db, #0e7c47)", color: "white", padding: "16px 24px", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
        <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>🏥 Medi-Cal Eligibility Agent</h1>
            <p style={{ margin: "4px 0 0", fontSize: 13, opacity: 0.9 }}>DHCS — AI-Powered Eligibility Screening</p>
          </div>
          <span style={{ fontSize: 12, background: health ? "rgba(255,255,255,0.2)" : "rgba(255,0,0,0.3)", padding: "4px 10px", borderRadius: 12 }}>
            {health ? `✓ Connected (${health.mock_mode ? "mock" : "live"})` : "✗ Offline"}
          </span>
        </div>
      </header>

      {/* Tabs */}
      <nav style={{ maxWidth: 800, margin: "0 auto", borderBottom: "1px solid #ddd", display: "flex", gap: 4, paddingTop: 4 }}>
        <button style={tabStyle("chat")} onClick={() => setActiveTab("chat")} data-testid="tab-chat">Chat</button>
        <button style={tabStyle("screening")} onClick={() => setActiveTab("screening")} data-testid="tab-screening">Screening</button>
        <button style={tabStyle("programs")} onClick={() => setActiveTab("programs")} data-testid="tab-programs">Programs</button>
      </nav>

      <main style={{ maxWidth: 800, margin: "0 auto", padding: 16 }}>
        {/* Chat Tab */}
        {activeTab === "chat" && (
          <>
            <div data-testid="chat-messages" style={{ minHeight: 400, maxHeight: "60vh", overflowY: "auto", marginBottom: 16 }}>
              {messages.length === 0 && (
                <div style={{ textAlign: "center", color: "#666", padding: "60px 20px" }}>
                  <p style={{ fontSize: 18 }}>Welcome! Ask me about Medi-Cal eligibility.</p>
                  <p style={{ fontSize: 14 }}>Try: &quot;I make $1,500/month and live alone. Am I eligible?&quot;</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} style={{ marginBottom: 12 }} data-testid={`message-${i}`}>
                  <div style={{
                    background: msg.role === "user" ? "#1a56db" : "white",
                    color: msg.role === "user" ? "white" : "#333",
                    padding: "12px 16px", borderRadius: 12,
                    maxWidth: "80%",
                    marginLeft: msg.role === "user" ? "auto" : 0,
                    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                  }}>
                    <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
                  </div>
                  {/* Eligibility Card */}
                  {msg.eligibility && (
                    <div style={{
                      background: msg.eligibility.likely_eligible ? "#ecfdf5" : "#fef2f2",
                      border: `1px solid ${msg.eligibility.likely_eligible ? "#10b981" : "#ef4444"}`,
                      borderRadius: 12, padding: 16, marginTop: 8, maxWidth: "80%",
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                        <span style={{ fontSize: 20 }}>{msg.eligibility.likely_eligible ? "✅" : "❌"}</span>
                        <strong>{msg.eligibility.likely_eligible ? "Likely Eligible" : "May Not Qualify"}</strong>
                        <span style={{ marginLeft: "auto", fontSize: 12, color: "#666" }}>
                          {msg.eligibility.program_type} • {msg.eligibility.fpl_percentage.toFixed(0)}% FPL
                        </span>
                      </div>
                      {msg.eligibility.next_steps.length > 0 && (
                        <div style={{ fontSize: 13 }}>
                          <strong>Next Steps:</strong>
                          <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
                            {msg.eligibility.next_steps.map((s, j) => <li key={j}>{s}</li>)}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div style={{ fontSize: 11, color: "#888", marginTop: 4, maxWidth: "80%" }}>
                      {msg.citations.map((c, j) => (
                        <span key={j} style={{ marginRight: 8 }}>📄 {c.source}{c.regulation_ref ? ` (${c.regulation_ref})` : ""}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {isLoading && <div style={{ color: "#888", padding: 8 }}>Analyzing...</div>}
              <div ref={messagesEnd} />
            </div>

            {/* Input */}
            <div style={{ display: "flex", gap: 8 }}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask about Medi-Cal eligibility..."
                data-testid="chat-input"
                style={{
                  flex: 1, padding: "12px 16px", borderRadius: 12,
                  border: "1px solid #ccc", fontSize: 15, outline: "none",
                }}
              />
              <button
                onClick={handleSend}
                disabled={isLoading}
                data-testid="chat-send"
                style={{
                  padding: "12px 24px", borderRadius: 12, border: "none",
                  background: "#1a56db", color: "white", fontWeight: 600,
                  cursor: isLoading ? "not-allowed" : "pointer", fontSize: 15,
                }}
              >
                Send
              </button>
            </div>
          </>
        )}

        {/* Screening Tab */}
        {activeTab === "screening" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <EligibilityScreener />
            <DocumentUpload />
          </div>
        )}

        {/* Programs Tab */}
        {activeTab === "programs" && <ProgramList />}
      </main>
      <Footer />
    </div>
  );
}
