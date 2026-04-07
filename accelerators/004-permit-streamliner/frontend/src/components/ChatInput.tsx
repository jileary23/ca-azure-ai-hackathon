import { useState, FormEvent } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about permits, zoning, fees..."
        disabled={disabled}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 disabled:opacity-50"
        aria-label="Message input"
        data-testid="chat-input"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        style={{ backgroundColor: "#1B2A4A" }}
        data-testid="chat-send"
      >
        {disabled ? "..." : "Send"}
      </button>
    </form>
  );
}
