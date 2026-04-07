export default function Footer() {
  return (
    <footer className="bg-gray-900 border-t border-gray-800 mt-auto" role="contentinfo">
      <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-gray-400">
        <div className="flex items-center gap-1.5">
          <span>Built by</span>
          <a
            href="https://github.com/msftsean"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-300 hover:text-white transition-colors underline underline-offset-2"
            aria-label="Sean Gayle on GitHub"
          >
            Sean Gayle
          </a>
        </div>
        <div className="flex items-center gap-1.5 text-gray-500">
          <span>☁️</span>
          <span>Powered by Microsoft Azure</span>
        </div>
      </div>
    </footer>
  );
}
