import { useEffect, useState } from 'react';
import { getIncidents } from '../api/apiClient';
import type { IncidentSummary } from '../types';

const severityColor = (s: string) => {
  const map: Record<string, string> = {
    minor: '#22c55e',
    moderate: '#f59e0b',
    major: '#ef4444',
    catastrophic: '#7c3aed',
  };
  return map[s] || '#888';
};

export default function IncidentList() {
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getIncidents()
      .then((data) => {
        setIncidents(Array.isArray(data) ? data : data.incidents ?? []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div data-testid="incident-list" style={{ color: '#888', padding: 12 }}>
        Loading incidents…
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="incident-list" style={{ color: '#ef4444', padding: 12, fontSize: 13 }}>
        ⚠ {error}
      </div>
    );
  }

  if (incidents.length === 0) {
    return (
      <div data-testid="incident-list" style={{ color: '#888', padding: 12, fontSize: 13 }}>
        No active incidents.
      </div>
    );
  }

  return (
    <div data-testid="incident-list">
      {incidents.map((inc) => (
        <div
          key={inc.incident_id}
          data-testid="incident-card"
          style={{
            background: '#2d2d44',
            border: `1px solid ${severityColor(inc.severity)}`,
            borderRadius: 10,
            padding: 12,
            marginBottom: 8,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span
              style={{
                display: 'inline-block',
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: severityColor(inc.severity),
              }}
            />
            <strong style={{ color: '#e0e0e0', fontSize: 14 }}>{inc.name}</strong>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: 11,
                background: severityColor(inc.severity),
                color: '#fff',
                padding: '2px 8px',
                borderRadius: 8,
                fontWeight: 600,
                textTransform: 'uppercase',
              }}
            >
              {inc.severity}
            </span>
          </div>
          <div style={{ fontSize: 12, color: '#aaa' }}>
            📍 {inc.location} &bull; {inc.containment_pct ?? 0}% contained &bull; {inc.lead_agency}
          </div>
        </div>
      ))}
    </div>
  );
}
