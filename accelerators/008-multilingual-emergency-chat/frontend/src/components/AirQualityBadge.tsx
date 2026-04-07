import { useEffect, useState } from "react";
import { getAirQuality } from "../api/apiClient";

interface AQIData {
  aqi: number;
  category?: string;
  pollutant?: string;
}

interface AQILevel {
  label: string;
  color: string;
  textColor: string;
  guidance: string;
}

function getAQILevel(aqi: number): AQILevel {
  if (aqi <= 50)
    return { label: "Good", color: "bg-green-500", textColor: "text-green-400", guidance: "Air quality is satisfactory." };
  if (aqi <= 100)
    return { label: "Moderate", color: "bg-yellow-500", textColor: "text-yellow-400", guidance: "Acceptable. Sensitive individuals may experience minor effects." };
  if (aqi <= 150)
    return { label: "Unhealthy for Sensitive Groups", color: "bg-orange-500", textColor: "text-orange-400", guidance: "Sensitive groups should reduce prolonged outdoor exertion." };
  if (aqi <= 200)
    return { label: "Unhealthy", color: "bg-red-500", textColor: "text-red-400", guidance: "Everyone may begin to experience health effects. Limit outdoor activity." };
  if (aqi <= 300)
    return { label: "Very Unhealthy", color: "bg-purple-600", textColor: "text-purple-400", guidance: "Health alert: everyone may experience serious effects. Avoid outdoor exertion." };
  return { label: "Hazardous", color: "bg-rose-900", textColor: "text-rose-400", guidance: "Emergency conditions. Everyone should avoid all outdoor activity." };
}

interface Props {
  zip?: string;
}

export default function AirQualityBadge({ zip }: Props) {
  const [data, setData] = useState<AQIData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getAirQuality(zip)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load AQI");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [zip]);

  if (loading) {
    return (
      <div data-testid="air-quality-badge" className="animate-pulse text-gray-400 text-sm">
        Loading AQI…
      </div>
    );
  }

  if (error) {
    return (
      <div data-testid="air-quality-badge" className="text-red-400 text-xs">
        AQI unavailable
      </div>
    );
  }

  if (!data) return null;

  const level = getAQILevel(data.aqi);

  return (
    <div data-testid="air-quality-badge" className="flex items-center gap-3 p-3 bg-gray-800 rounded-lg border border-gray-700">
      <div className={`${level.color} text-white rounded-lg w-14 h-14 flex flex-col items-center justify-center`}>
        <span className="text-lg font-bold leading-none">{data.aqi}</span>
        <span className="text-[8px] uppercase tracking-wide">AQI</span>
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-semibold ${level.textColor}`}>{level.label}</p>
        <p className="text-xs text-gray-400 mt-0.5">{level.guidance}</p>
        {data.pollutant && (
          <p className="text-[10px] text-gray-500 mt-0.5">Primary: {data.pollutant}</p>
        )}
      </div>
    </div>
  );
}
