import { useEffect, useState } from 'react';
import { getEvacuationZones } from '../api/apiClient';
import type { EvacZone } from '../types';

const statusColor = (status: string) => {
  const map: Record<string, string> = {
    mandatory: '#ef4444',
    warning: '#f59e0b',
    advisory: '#3b82f6',
    clear: '#22c55e',
  };
  return map[status.toLowerCase()] || '#888';
};

export default function EvacuationPanel() {
  const [zones, setZones] = useState<EvacZone[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEvacuationZones()
      .then((data) => {
        setZones(Array.isArray(data) ? data : data.zones ?? []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div data-testid="evacuation-panel" style={{ color: '#888', padding: 12 }}>
        Loading evacuation zones…
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="evacuation-panel" style={{ color: '#ef4444', padding: 12, fontSize: 13 }}>
        ⚠ {error}
      </div>
    );
  }

  if (zones.length === 0) {
    return (
      <div data-testid="evacuation-panel" style={{ color: '#888', padding: 12, fontSize: 13 }}>
        No active evacuation zones.
      </div>
    );
  }

  return (
    <div data-testid="evacuation-panel">
      {zones.map((zone) => (
        <div
          key={zone.zone_id}
          style={{
            background: '#2d2d44',
            borderLeft: `4px solid ${statusColor(zone.status)}`,
            borderRadius: 8,
            padding: 12,
            marginBottom: 8,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <strong style={{ color: '#e0e0e0', fontSize: 14 }}>{zone.zone_name}</strong>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: 11,
                background: statusColor(zone.status),
                color: '#fff',
                padding: '2px 8px',
                borderRadius: 8,
                fontWeight: 600,
                textTransform: 'uppercase',
              }}
            >
              {zone.status}
            </span>
          </div>
          <div style={{ fontSize: 12, color: '#aaa', marginBottom: 4 }}>
            Population: {zone.population.toLocaleString()}
          </div>
          {zone.routes.length > 0 && (
            <div style={{ fontSize: 12, color: '#aaa' }}>
              🛣 Routes: {zone.routes.join(', ')}
            </div>
          )}
          {zone.shelters.length > 0 && (
            <div style={{ fontSize: 12, color: '#aaa' }}>
              🏠 Shelters: {zone.shelters.join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
