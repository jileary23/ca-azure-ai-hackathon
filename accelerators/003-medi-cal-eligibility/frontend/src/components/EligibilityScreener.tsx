import React, { useState } from 'react';
import { screenEligibility } from '../api/apiClient';
import type { EligibilityResult } from '../types';

export default function EligibilityScreener() {
  const [householdSize, setHouseholdSize] = useState(1);
  const [monthlyIncome, setMonthlyIncome] = useState(0);
  const [age, setAge] = useState(30);
  const [pregnant, setPregnant] = useState(false);
  const [disabled, setDisabled] = useState(false);
  const [county, setCounty] = useState('');
  const [result, setResult] = useState<EligibilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await screenEligibility({
        household_size: householdSize,
        monthly_income: monthlyIncome,
        age,
        pregnant: pregnant || undefined,
        disabled: disabled || undefined,
        county: county || undefined,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Screening failed');
    } finally {
      setLoading(false);
    }
  };

  const labelStyle: React.CSSProperties = {
    display: 'block', marginBottom: 12, fontSize: 14, color: '#333',
  };
  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '8px 12px', borderRadius: 8,
    border: '1px solid #ccc', fontSize: 14, marginTop: 4, boxSizing: 'border-box',
  };

  return (
    <div style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <h3 style={{ margin: '0 0 16px', color: '#1a56db' }}>Medi-Cal Eligibility Screener</h3>
      <form onSubmit={handleSubmit} data-testid="eligibility-screener">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <label style={labelStyle}>
            Household Size
            <input type="number" min={1} value={householdSize} onChange={e => setHouseholdSize(Number(e.target.value))}
              style={inputStyle} data-testid="screener-household-size" />
          </label>
          <label style={labelStyle}>
            Monthly Income ($)
            <input type="number" min={0} value={monthlyIncome} onChange={e => setMonthlyIncome(Number(e.target.value))}
              style={inputStyle} data-testid="screener-monthly-income" />
          </label>
          <label style={labelStyle}>
            Age
            <input type="number" min={0} value={age} onChange={e => setAge(Number(e.target.value))}
              style={inputStyle} data-testid="screener-age" />
          </label>
          <label style={labelStyle}>
            County
            <input type="text" value={county} onChange={e => setCounty(e.target.value)}
              placeholder="e.g. Los Angeles" style={inputStyle} data-testid="screener-county" />
          </label>
        </div>
        <div style={{ display: 'flex', gap: 24, margin: '12px 0' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 14, cursor: 'pointer' }}>
            <input type="checkbox" checked={pregnant} onChange={e => setPregnant(e.target.checked)}
              data-testid="screener-pregnant" /> Pregnant
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 14, cursor: 'pointer' }}>
            <input type="checkbox" checked={disabled} onChange={e => setDisabled(e.target.checked)}
              data-testid="screener-disabled" /> Disabled
          </label>
        </div>
        <button type="submit" disabled={loading} data-testid="screener-submit" style={{
          padding: '10px 24px', borderRadius: 8, border: 'none',
          background: '#1a56db', color: 'white', fontWeight: 600, fontSize: 14,
          cursor: loading ? 'not-allowed' : 'pointer', marginTop: 8,
        }}>
          {loading ? 'Screening...' : 'Screen Eligibility'}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: 16, padding: 12, background: '#fef2f2', border: '1px solid #ef4444', borderRadius: 8, color: '#b91c1c', fontSize: 14 }}
          data-testid="screener-error">
          {error}
        </div>
      )}

      {result && (
        <div data-testid="screener-result" style={{
          marginTop: 16, padding: 16, borderRadius: 12,
          background: result.likely_eligible ? '#ecfdf5' : '#fef2f2',
          border: `1px solid ${result.likely_eligible ? '#10b981' : '#ef4444'}`,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 20 }}>{result.likely_eligible ? '✅' : '❌'}</span>
            <strong>{result.likely_eligible ? 'Likely Eligible' : 'May Not Qualify'}</strong>
            <span style={{ marginLeft: 'auto', fontSize: 12, color: '#666' }}>
              {result.program_type} • {result.fpl_percentage.toFixed(0)}% FPL • Confidence: {(result.confidence * 100).toFixed(0)}%
            </span>
          </div>
          {result.factors.length > 0 && (
            <div style={{ fontSize: 13, marginBottom: 8 }}>
              <strong>Factors:</strong>
              <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                {result.factors.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
          )}
          {result.required_documents.length > 0 && (
            <div style={{ fontSize: 13, marginBottom: 8 }}>
              <strong>Required Documents:</strong>
              <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                {result.required_documents.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </div>
          )}
          {result.next_steps.length > 0 && (
            <div style={{ fontSize: 13 }}>
              <strong>Next Steps:</strong>
              <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                {result.next_steps.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
