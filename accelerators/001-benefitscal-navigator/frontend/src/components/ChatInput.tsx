import { useState, FormEvent } from "react";

const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "es", name: "Español" },
  { code: "zh", name: "中文" },
  { code: "vi", name: "Tiếng Việt" },
  { code: "tl", name: "Tagalog" },
  { code: "ko", name: "한국어" },
  { code: "hy", name: "Հայերեն" },
  { code: "fa", name: "فارسی" },
  { code: "ar", name: "العربية" },
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
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="rounded-lg border border-gray-300 px-2 py-2 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        aria-label="Select language"
        data-testid="language-select"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about California benefits..."
        disabled={disabled}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
        aria-label="Message input"
        data-testid="chat-input"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        data-testid="chat-send"
        className="bg-blue-700 hover:bg-blue-800 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? "..." : "Send"}
      </button>
    </form>
  );
}
