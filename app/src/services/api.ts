// API service for connecting to the backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Types matching backend schemas
export interface Zone {
  id: string;
  name: string;
  coordinates: number[][];
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  damage_score: number;
  survival_probability: number;
  population: number;
  priority_score: number;
  incident_id: string;
}

export interface Resource {
  id: string;
  type: 'ambulance' | 'rescue_team' | 'drone' | 'fire_truck';
  name: string;
  status: 'available' | 'deployed' | 'maintenance';
  latitude?: number;
  longitude?: number;
  capacity: number;
  current_load: number;
  zone_id?: string;
}

export interface Incident {
  id: string;
  type: string;
  title: string;
  description?: string;
  latitude: number;
  longitude: number;
  severity: number;
  status: 'active' | 'contained' | 'resolved';
  started_at: string;
  zones: Zone[];
}

export interface TimelineEvent {
  id: string;
  event_type: string;
  title: string;
  description?: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp: string;
  zone_id?: string;
}

export interface Recommendation {
  id: string;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  reasoning?: string;
  status: 'pending' | 'executed' | 'dismissed';
  zone_id?: string;
}

export interface AnalysisResult {
  id: string;
  analysis_type: string;
  results: Record<string, unknown>;
  confidence: number;
  explanation?: string;
  bounding_boxes?: BoundingBox[];
  heatmap_url?: string;
  created_at: string;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}

export interface DashboardStats {
  total_incidents: number;
  active_incidents: number;
  critical_zones: number;
  total_population_at_risk: number;
  available_resources: number;
  deployed_resources: number;
  pending_recommendations: number;
}

export interface RiskAssessment {
  zone_id: string;
  metrics: {
    damage_severity: number;
    survival_probability: number;
    threat_level: string;
    priority_score: number;
  };
  factors: Record<string, number>;
}

// API client class
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${this.baseUrl.replace('/api/v1', '')}/health`);
    return response.json();
  }

  // Incidents
  async getIncidents(status?: string): Promise<Incident[]> {
    const params = status ? `?status=${status}` : '';
    return this.fetch(`/incidents${params}`);
  }

  async getIncident(id: string): Promise<Incident> {
    return this.fetch(`/incidents/${id}`);
  }

  async createIncident(incident: Partial<Incident>): Promise<Incident> {
    return this.fetch('/incidents', {
      method: 'POST',
      body: JSON.stringify(incident),
    });
  }

  // Zones
  async getZones(incidentId?: string): Promise<Zone[]> {
    const params = incidentId ? `?incident_id=${incidentId}` : '';
    return this.fetch(`/zones${params}`);
  }

  async createZone(zone: Partial<Zone>): Promise<Zone> {
    return this.fetch('/zones', {
      method: 'POST',
      body: JSON.stringify(zone),
    });
  }

  // Resources
  async getResources(status?: string, type?: string): Promise<Resource[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (type) params.append('type', type);
    return this.fetch(`/resources?${params.toString()}`);
  }

  async assignResource(resourceId: string, zoneId: string): Promise<void> {
    return this.fetch(`/resources/${resourceId}/assign?zone_id=${zoneId}`, {
      method: 'POST',
    });
  }

  // Analysis
  async analyzeImage(file: File, incidentId?: string, zoneId?: string): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (incidentId) formData.append('incident_id', incidentId);
    if (zoneId) formData.append('zone_id', zoneId);

    const response = await fetch(`${this.baseUrl}/analyze/image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(error.detail);
    }

    return response.json();
  }

  async analyzeText(text: string, source: string = 'manual'): Promise<AnalysisResult> {
    return this.fetch(`/analyze/text?text=${encodeURIComponent(text)}&source=${source}`, {
      method: 'POST',
    });
  }

  // Risk Assessment
  async getZoneRisk(zoneId: string): Promise<RiskAssessment> {
    return this.fetch(`/risk/zone/${zoneId}`);
  }

  // Recommendations
  async getRecommendations(incidentId?: string, status?: string): Promise<Recommendation[]> {
    const params = new URLSearchParams();
    if (incidentId) params.append('incident_id', incidentId);
    if (status) params.append('status', status);
    return this.fetch(`/recommendations?${params.toString()}`);
  }

  async generateRecommendations(zoneId: string): Promise<{ recommendations: Recommendation[] }> {
    return this.fetch(`/recommendations/generate/${zoneId}`, {
      method: 'POST',
    });
  }

  async executeRecommendation(recommendationId: string, executedBy: string): Promise<void> {
    return this.fetch(`/recommendations/${recommendationId}/execute`, {
      method: 'POST',
      body: JSON.stringify({ executed_by: executedBy }),
    });
  }

  // Timeline
  async getTimeline(incidentId: string, limit: number = 50): Promise<TimelineEvent[]> {
    return this.fetch(`/timeline/${incidentId}?limit=${limit}`);
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    return this.fetch('/dashboard/stats');
  }

  async getMapData(incidentId?: string): Promise<{
    zones: Zone[];
    resources: Resource[];
    incidents: Incident[];
  }> {
    const params = incidentId ? `?incident_id=${incidentId}` : '';
    return this.fetch(`/dashboard/map${params}`);
  }

  // Agentic AI Multi-Agent Endpoints
  async getAgentHealth(): Promise<{ status: string; agents: string[]; llm: Record<string, unknown> }> {
    return this.fetch('/agents/health');
  }

  async runAgentWorkflow(incidentId: string): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/run-agent-workflow`, {
      method: 'POST',
    });
  }

  async getAgentStatus(incidentId: string): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/agent-status`);
  }

  async getCriticResult(incidentId: string): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/critic-result`);
  }

  async getDecisionPlan(incidentId: string): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/decision-plan`);
  }

  async getAuditLog(incidentId: string): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/audit-log`);
  }

  async approvePlan(
    incidentId: string,
    action: string = 'APPROVE',
    approver: string = 'Incident Commander',
    role: string = 'Commander',
    comments?: string,
    overrideReason?: string
  ): Promise<Record<string, unknown>> {
    let url = `/incidents/${incidentId}/approve?action=${encodeURIComponent(action)}&approver=${encodeURIComponent(approver)}&role=${encodeURIComponent(role)}`;
    if (comments) url += `&comments=${encodeURIComponent(comments)}`;
    if (overrideReason) url += `&override_reason=${encodeURIComponent(overrideReason)}`;
    return this.fetch(url, { method: 'POST' });
  }

  async rejectPlan(incidentId: string, reason: string = 'Revision requested', approver: string = 'Incident Commander'): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/reject?reason=${encodeURIComponent(reason)}&approver=${encodeURIComponent(approver)}`, {
      method: 'POST',
    });
  }

  async modifyPlan(incidentId: string, modifications: Record<string, unknown>): Promise<Record<string, unknown>> {
    return this.fetch(`/incidents/${incidentId}/modify`, {
      method: 'POST',
      body: JSON.stringify(modifications),
    });
  }
}

// Export singleton instance
export const api = new ApiClient(API_BASE_URL);

// Derive WebSocket URL dynamically from API_BASE_URL or window location
const getWebSocketUrl = (): string => {
  const envUrl = import.meta.env.VITE_WS_URL;
  if (envUrl) return envUrl;
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host || 'localhost:8000';
  return `${protocol}//${host.split(':')[0]}:8000/ws`;
};

// WebSocket client
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number = 5000;
  private messageHandlers: ((data: unknown) => void)[] = [];

  constructor(url: string = getWebSocketUrl()) {
    this.url = url;
  }

  connect(): void {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.messageHandlers.forEach(handler => handler(data));
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected, reconnecting...');
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: unknown): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  onMessage(handler: (data: unknown) => void): void {
    this.messageHandlers.push(handler);
  }

  offMessage(handler: (data: unknown) => void): void {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }
}
