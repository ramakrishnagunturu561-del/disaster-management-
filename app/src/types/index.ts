export interface Zone {
  id: string;
  name: string;
  coordinates: [number, number][];
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  damageScore: number;
  survivalProbability: number;
  population: number;
  lastUpdated: Date;
}

export interface RiskMetrics {
  damageSeverity: number;
  survivalProbability: number;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
}

export interface Resource {
  id: string;
  type: 'ambulance' | 'rescue_team' | 'drone' | 'fire_truck';
  status: 'available' | 'deployed' | 'maintenance';
  location?: [number, number];
  assignment?: string;
}

export interface Recommendation {
  id: string;
  category: 'rescue' | 'evacuation' | 'surveillance' | 'medical';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  reasoning: string;
  zoneId: string;
  timestamp: Date;
  status: 'pending' | 'executed' | 'dismissed';
}

export interface TimelineEvent {
  id: string;
  timestamp: Date;
  type: 'incident' | 'alert' | 'action' | 'update';
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  zoneId?: string;
}

export interface DamageDetection {
  id: string;
  imageUrl: string;
  boundingBoxes: BoundingBox[];
  heatmapData: number[][];
  damageScore: number;
  confidence: number;
  explanation: string;
  timestamp: Date;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}

export interface SensorData {
  id: string;
  type: 'seismic' | 'temperature' | 'radiation' | 'flood';
  value: number;
  unit: string;
  location: [number, number];
  timestamp: Date;
  anomaly: boolean;
}

export interface SocialMediaReport {
  id: string;
  platform: string;
  content: string;
  location?: [number, number];
  sentiment: 'negative' | 'neutral' | 'positive';
  urgency: boolean;
  timestamp: Date;
}

export interface Incident {
  id: string;
  type: 'earthquake' | 'flood' | 'fire' | 'hurricane' | 'terrorism' | 'industrial';
  status: 'active' | 'contained' | 'resolved';
  location: [number, number];
  severity: number;
  startedAt: Date;
  description: string;
}
