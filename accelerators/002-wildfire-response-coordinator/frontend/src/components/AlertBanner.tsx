import { useEffect, useState } from 'react';
import { getWeatherAlerts } from '../api/apiClient';
import type { WeatherAlert } from '../types';

const alertColor = (severity: string) => {
  const map: Record<string, string> = {
    extreme: '#dc2626',
    severe: '#ef4444',
    moderate: '#f59e0b',
    minor: '#eab308',
  };
  return map[severity.toLowerCase()] || '#f59e0b';
};

export default function AlertBanner() {
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getWeatherAlerts()
      .then((data) => {
        setAlerts(Array.isArray(data) ? data : data.alerts ?? []);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error || alerts.length === 0) return null;

  return (
    <div data-testid="alert-banner">
      {alerts.map((alert) => (
        <div
          key={alert.alert_id}
          style={{
            background: alertColor(alert.severity),
            color: '#fff',
            padding: '10px 16px',
            borderRadius: 8,
            marginBottom: 8,
            fontSize: 13,
            boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <strong>⚠ {alert.title}</strong>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: 11,
                opacity: 0.85,
                textTransform: 'uppercase',
              }}
            >
              {alert.severity}
            </span>
          </div>
          <div style={{ fontSize: 12, opacity: 0.9 }}>{alert.description}</div>
          {alert.areas.length > 0 && (
            <div style={{ fontSize: 11, marginTop: 4, opacity: 0.8 }}>
              Areas: {alert.areas.join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
