export interface HealthStatus {
  status: string;
  service: string;
  mock_mode: boolean;
}

export interface IncidentSummary {
  incident_id: string;
  name: string;
  incident_type: string;
  severity: string;
  location: string;
  containment_pct: number | null;
  status: string;
  lead_agency: string;
}

export interface EvacZone {
  zone_id: string;
  zone_name: string;
  status: string;
  population: number;
  routes: string[];
  shelters: string[];
}

export interface EvacInfo {
  zones: EvacZone[];
  total_evacuated: number;
  shelters_open: number;
}

export interface Resource {
  resource_id: string;
  resource_type: string;
  quantity: number;
  agency: string;
  status: string;
}

export interface Citation {
  source: string;
  text: string;
  agency: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  incident?: IncidentSummary | null;
  evacuation?: EvacInfo | null;
  resources?: Resource[] | null;
  citations?: Citation[];
}

export interface WeatherAlert {
  alert_id: string;
  title: string;
  severity: string;
  description: string;
  effective: string;
  expires: string;
  areas: string[];
}
