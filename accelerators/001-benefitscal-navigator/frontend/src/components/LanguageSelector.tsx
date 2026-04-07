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
  value: string;
  onChange: (lang: string) => void;
}

export default function LanguageSelector({ value, onChange }: Props) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      data-testid="language-selector"
      aria-label="Select language"
      className="rounded-lg border border-gray-300 px-2 py-2 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
    >
      {LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.name}
        </option>
      ))}
    </select>
  );
}
