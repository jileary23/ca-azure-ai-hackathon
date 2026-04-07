import { useEffect, useState } from 'react';
import { getPrograms } from '../api/apiClient';
import type { MediCalProgram } from '../types';

export default function ProgramList() {
  const [programs, setPrograms] = useState<MediCalProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPrograms()
      .then(data => {
        setPrograms(Array.isArray(data) ? data : data.programs ?? []);
      })
      .catch(err => setError(err instanceof Error ? err.message : 'Failed to load programs'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign: 'center', padding: 40, color: '#666' }}>Loading programs...</div>;
  if (error) return (
    <div style={{ padding: 16, background: '#fef2f2', border: '1px solid #ef4444', borderRadius: 12, color: '#b91c1c', fontSize: 14 }}
      data-testid="program-list-error">
      {error}
    </div>
  );

  return (
    <div data-testid="program-list">
      <h3 style={{ margin: '0 0 16px', color: '#1a56db' }}>Medi-Cal Program Variants</h3>
      {programs.length === 0 && <p style={{ color: '#666' }}>No programs found.</p>}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {programs.map(p => (
          <div key={p.program_id} data-testid={`program-${p.program_id}`} style={{
            background: 'white', borderRadius: 12, padding: 20,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #1a56db',
          }}>
            <h4 style={{ margin: '0 0 6px', color: '#1a56db' }}>{p.name}</h4>
            <p style={{ margin: '0 0 8px', fontSize: 14, color: '#555' }}>{p.description}</p>
            <div style={{ display: 'flex', gap: 24, fontSize: 13, color: '#666' }}>
              <span><strong>Eligibility:</strong> {p.eligibility_criteria}</span>
              <span><strong>Income Limit:</strong> {p.income_limit}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
