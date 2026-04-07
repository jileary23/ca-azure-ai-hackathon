import React, { useState } from 'react';
import { analyzeDocument } from '../api/apiClient';

interface AnalysisResult {
  document_type: string;
  file_name: string;
  status: string;
  [key: string]: unknown;
}

const DOCUMENT_TYPES = [
  { value: 'proof_of_income', label: 'Proof of Income' },
  { value: 'proof_of_identity', label: 'Proof of Identity' },
  { value: 'proof_of_residency', label: 'Proof of Residency' },
  { value: 'immigration_status', label: 'Immigration Status' },
  { value: 'other', label: 'Other' },
];

export default function DocumentUpload() {
  const [documentType, setDocumentType] = useState('proof_of_income');
  const [fileName, setFileName] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileName.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeDocument({ document_type: documentType, file_name: fileName });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Document analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '8px 12px', borderRadius: 8,
    border: '1px solid #ccc', fontSize: 14, marginTop: 4, boxSizing: 'border-box',
  };

  return (
    <div style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
      data-testid="document-upload">
      <h3 style={{ margin: '0 0 16px', color: '#0e7c47' }}>Document Analysis (Mock)</h3>
      <form onSubmit={handleSubmit}>
        <label style={{ display: 'block', marginBottom: 12, fontSize: 14, color: '#333' }}>
          Document Type
          <select value={documentType} onChange={e => setDocumentType(e.target.value)}
            style={{ ...inputStyle, appearance: 'auto' }} data-testid="document-type-select">
            {DOCUMENT_TYPES.map(dt => (
              <option key={dt.value} value={dt.value}>{dt.label}</option>
            ))}
          </select>
        </label>
        <label style={{ display: 'block', marginBottom: 12, fontSize: 14, color: '#333' }}>
          File Name
          <input type="text" value={fileName} onChange={e => setFileName(e.target.value)}
            placeholder="e.g. pay_stub_march.pdf" style={inputStyle} data-testid="document-file-name" />
        </label>
        <button type="submit" disabled={loading || !fileName.trim()} data-testid="document-submit" style={{
          padding: '10px 24px', borderRadius: 8, border: 'none',
          background: '#0e7c47', color: 'white', fontWeight: 600, fontSize: 14,
          cursor: loading || !fileName.trim() ? 'not-allowed' : 'pointer',
        }}>
          {loading ? 'Analyzing...' : 'Analyze Document'}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: 16, padding: 12, background: '#fef2f2', border: '1px solid #ef4444', borderRadius: 8, color: '#b91c1c', fontSize: 14 }}
          data-testid="document-error">
          {error}
        </div>
      )}

      {result && (
        <div data-testid="document-result" style={{
          marginTop: 16, padding: 16, borderRadius: 12,
          background: '#ecfdf5', border: '1px solid #10b981',
        }}>
          <strong>Analysis Result</strong>
          <pre style={{ margin: '8px 0 0', fontSize: 13, whiteSpace: 'pre-wrap', color: '#333' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
