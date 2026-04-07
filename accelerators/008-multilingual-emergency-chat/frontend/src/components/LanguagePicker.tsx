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
  { code: "hi", label: "हिन्दी" },
  { code: "th", label: "ไทย" },
  { code: "km", label: "ភាសាខ្មែរ" },
  { code: "lo", label: "ລາວ" },
  { code: "my", label: "မြန်မာ" },
  { code: "am", label: "አማርኛ" },
];

interface Props {
  value: string;
  onChange: (lang: string) => void;
}

export default function LanguagePicker({ value, onChange }: Props) {
  return (
    <div data-testid="language-picker" className="flex flex-wrap gap-1.5">
      {LANGUAGES.map((l) => (
        <button
          key={l.code}
          type="button"
          onClick={() => onChange(l.code)}
          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            value === l.code
              ? "bg-orange-600 text-white shadow-sm"
              : "bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-600"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}
