import { useState, FormEvent } from "react";

interface Props {
  onSend: (message: string, language: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed, "en");
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Search across California state agencies..."
        disabled={disabled}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-blue-800 focus:border-blue-800 disabled:opacity-50"
        aria-label="Message input"
        data-testid="chat-input"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="bg-blue-900 hover:bg-blue-800 text-amber-100 rounded-lg px-5 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        data-testid="chat-send"
      >
        {disabled ? "..." : "Search"}
      </button>
    </form>
  );
}
