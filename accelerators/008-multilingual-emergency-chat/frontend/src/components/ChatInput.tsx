import { useState, type FormEvent } from "react";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
  { code: "zh", label: "中文" },
  { code: "vi", label: "Tiếng Việt" },
  { code: "tl", label: "Tagalog" },
  { code: "ko", label: "한국어" },
  { code: "ar", label: "العربية" },
  { code: "ja", label: "日本語" },
  { code: "ru", label: "Русский" },
];

interface Props {
  onSend: (message: string, language: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState("en");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed, language);
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-3 border-t bg-white">
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="rounded-lg border border-gray-300 px-2 py-2 text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-400"
        aria-label="Language"
        data-testid="language-select"
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>

      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about emergencies, shelters, air quality…"
        disabled={disabled}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 disabled:opacity-50"
        data-testid="chat-input"
      />

      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-300 text-white rounded-lg px-5 py-2 text-sm font-medium transition-colors"
        data-testid="chat-send"
      >
        Send
      </button>
    </form>
  );
}
