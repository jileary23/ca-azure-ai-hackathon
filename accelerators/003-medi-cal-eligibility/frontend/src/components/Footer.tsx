export default function Footer() {
  return (
    <footer
      style={{
        backgroundColor: "#111827",
        borderTop: "1px solid #1f2937",
        marginTop: "auto",
        padding: "12px 24px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: 24,
        fontSize: 12,
        color: "#9ca3af",
        fontFamily: "system-ui, sans-serif",
      }}
      role="contentinfo"
    >
      <span>
        Built by{" "}
        <a
          href="https://github.com/msftsean"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "#d1d5db", textDecoration: "underline", textUnderlineOffset: 2 }}
          aria-label="Sean Gayle on GitHub"
        >
          Sean Gayle
        </a>
      </span>
      <span style={{ color: "#4b5563" }}>·</span>
      <span style={{ color: "#6b7280" }}>☁️ Powered by Microsoft Azure</span>
    </footer>
  );
}
