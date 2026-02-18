import { useState, useEffect, useCallback } from 'react';
import type { 
  Zone, Resource, Recommendation, TimelineEvent, 
  SensorData, SocialMediaReport, Incident 
} from '@/types';

// Mock data generators
const generateZones = (): Zone[] => [
  {
    id: 'zone-1',
    name: 'Downtown District',
    coordinates: [
      [40.7128, -74.0060],
      [40.7150, -74.0060],
      [40.7150, -74.0030],
      [40.7128, -74.0030],
    ],
    riskLevel: 'critical',
    damageScore: 85,
    survivalProbability: 45,
    population: 15000,
    lastUpdated: new Date(),
  },
  {
    id: 'zone-2',
    name: 'Industrial Area',
    coordinates: [
      [40.7100, -74.0100],
      [40.7120, -74.0100],
      [40.7120, -74.0070],
      [40.7100, -74.0070],
    ],
    riskLevel: 'high',
    damageScore: 65,
    survivalProbability: 70,
    population: 5000,
    lastUpdated: new Date(),
  },
  {
    id: 'zone-3',
    name: 'Residential North',
    coordinates: [
      [40.7150, -74.0080],
      [40.7170, -74.0080],
      [40.7170, -74.0050],
      [40.7150, -74.0050],
    ],
    riskLevel: 'medium',
    damageScore: 35,
    survivalProbability: 85,
    population: 25000,
    lastUpdated: new Date(),
  },
  {
    id: 'zone-4',
    name: 'Safe Zone East',
    coordinates: [
      [40.7130, -74.0000],
      [40.7150, -74.0000],
      [40.7150, -73.9970],
      [40.7130, -73.9970],
    ],
    riskLevel: 'low',
    damageScore: 10,
    survivalProbability: 95,
    population: 12000,
    lastUpdated: new Date(),
  },
];

const generateResources = (): Resource[] => [
  { id: 'amb-1', type: 'ambulance', status: 'available', location: [40.7140, -74.0050] },
  { id: 'amb-2', type: 'ambulance', status: 'deployed', location: [40.7120, -74.0040], assignment: 'zone-1' },
  { id: 'amb-3', type: 'ambulance', status: 'available', location: [40.7160, -74.0060] },
  { id: 'amb-4', type: 'ambulance', status: 'deployed', location: [40.7110, -74.0080], assignment: 'zone-2' },
  { id: 'rescue-1', type: 'rescue_team', status: 'available', location: [40.7145, -74.0045] },
  { id: 'rescue-2', type: 'rescue_team', status: 'deployed', location: [40.7130, -74.0050], assignment: 'zone-1' },
  { id: 'rescue-3', type: 'rescue_team', status: 'deployed', location: [40.7115, -74.0085], assignment: 'zone-2' },
  { id: 'drone-1', type: 'drone', status: 'available', location: [40.7150, -74.0030] },
  { id: 'drone-2', type: 'drone', status: 'deployed', location: [40.7125, -74.0055], assignment: 'zone-1' },
  { id: 'drone-3', type: 'drone', status: 'deployed', location: [40.7105, -74.0075], assignment: 'zone-2' },
  { id: 'fire-1', type: 'fire_truck', status: 'available', location: [40.7140, -74.0060] },
  { id: 'fire-2', type: 'fire_truck', status: 'deployed', location: [40.7110, -74.0090], assignment: 'zone-2' },
];

const generateRecommendations = (): Recommendation[] => [
  {
    id: 'rec-1',
    category: 'rescue',
    priority: 'critical',
    title: 'Deploy Heavy Rescue Team',
    description: 'Deploy 2 rescue teams with heavy equipment to Downtown District for structural collapse response.',
    reasoning: 'AI analysis detected 3 building collapses with 85% damage severity. Thermal imaging indicates potential survivors. Time-critical: Golden hour approaching.',
    zoneId: 'zone-1',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    status: 'pending',
  },
  {
    id: 'rec-2',
    category: 'evacuation',
    priority: 'high',
    title: 'Evacuate Residential North',
    description: 'Initiate immediate evacuation of Residential North zone due to gas leak risk.',
    reasoning: 'Sensor data indicates gas concentration at 15% LEL. Wind direction changing. 25,000 population at risk.',
    zoneId: 'zone-3',
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    status: 'executed',
  },
  {
    id: 'rec-3',
    category: 'surveillance',
    priority: 'medium',
    title: 'Activate Drone Grid 2',
    description: 'Deploy drone surveillance to Industrial Area for ongoing hazard assessment.',
    reasoning: 'Chemical storage facility in zone. Need continuous monitoring for secondary incidents.',
    zoneId: 'zone-2',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    status: 'executed',
  },
  {
    id: 'rec-4',
    category: 'medical',
    priority: 'critical',
    title: 'Request Additional Ambulances',
    description: 'Request 3 additional ambulances from neighboring jurisdictions.',
    reasoning: 'Current capacity insufficient for projected casualties. Model predicts 45+ injured requiring transport.',
    zoneId: 'zone-1',
    timestamp: new Date(Date.now() - 1000 * 60 * 10),
    status: 'pending',
  },
];

const generateTimelineEvents = (): TimelineEvent[] => [
  {
    id: 'evt-1',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    type: 'incident',
    title: 'Earthquake Detected',
    description: 'Magnitude 6.8 earthquake detected 15km from city center.',
    severity: 'critical',
  },
  {
    id: 'evt-2',
    timestamp: new Date(Date.now() - 1000 * 60 * 55),
    type: 'alert',
    title: 'Building Collapse Reported',
    description: 'Multiple building collapses reported in Downtown District.',
    severity: 'critical',
    zoneId: 'zone-1',
  },
  {
    id: 'evt-3',
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
    type: 'action',
    title: 'Rescue Teams Deployed',
    description: '3 rescue teams deployed to priority zones.',
    severity: 'info',
  },
  {
    id: 'evt-4',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    type: 'update',
    title: 'Gas Leak Detected',
    description: 'Gas leak detected in Industrial Area. Evacuation initiated.',
    severity: 'warning',
    zoneId: 'zone-2',
  },
  {
    id: 'evt-5',
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    type: 'alert',
    title: 'Social Media Distress Signals',
    description: 'AI detected 23 distress messages from Residential North.',
    severity: 'warning',
    zoneId: 'zone-3',
  },
  {
    id: 'evt-6',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    type: 'action',
    title: 'Drone Surveillance Activated',
    description: 'Drone Grid 1 activated for Downtown District assessment.',
    severity: 'info',
    zoneId: 'zone-1',
  },
];

const generateSensorData = (): SensorData[] => [
  { id: 'sens-1', type: 'seismic', value: 6.8, unit: 'Magnitude', location: [40.7100, -74.0200], timestamp: new Date(), anomaly: true },
  { id: 'sens-2', type: 'temperature', value: 145, unit: '°C', location: [40.7120, -74.0080], timestamp: new Date(), anomaly: true },
  { id: 'sens-3', type: 'radiation', value: 0.12, unit: 'μSv/h', location: [40.7140, -74.0060], timestamp: new Date(), anomaly: false },
  { id: 'sens-4', type: 'flood', value: 2.3, unit: 'm', location: [40.7110, -74.0090], timestamp: new Date(), anomaly: true },
];

const generateSocialReports = (): SocialMediaReport[] => [
  { id: 'soc-1', platform: 'Twitter', content: 'Building collapsed near 5th Ave, people trapped inside! #earthquake #help', location: [40.7128, -74.0060], sentiment: 'negative', urgency: true, timestamp: new Date(Date.now() - 1000 * 60 * 50) },
  { id: 'soc-2', platform: 'Facebook', content: 'Need medical assistance at Downtown Community Center', location: [40.7135, -74.0055], sentiment: 'negative', urgency: true, timestamp: new Date(Date.now() - 1000 * 60 * 40) },
  { id: 'soc-3', platform: 'Twitter', content: 'Safe zone established at East Park. Follow official guidance. #safety', location: [40.7140, -73.9980], sentiment: 'positive', urgency: false, timestamp: new Date(Date.now() - 1000 * 60 * 25) },
];

const generateIncident = (): Incident => ({
  id: 'inc-1',
  type: 'earthquake',
  status: 'active',
  location: [40.7100, -74.0200],
  severity: 8,
  startedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
  description: 'Magnitude 6.8 earthquake with multiple aftershocks. Significant infrastructure damage reported.',
});

export function useDashboardData() {
  const [zones] = useState<Zone[]>(generateZones());
  const [resources] = useState<Resource[]>(generateResources());
  const [recommendations, setRecommendations] = useState<Recommendation[]>(generateRecommendations());
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>(generateTimelineEvents());
  const [sensorData, setSensorData] = useState<SensorData[]>(generateSensorData());
  const [socialReports] = useState<SocialMediaReport[]>(generateSocialReports());
  const [incident] = useState<Incident>(generateIncident());
  const [isSimulating, setIsSimulating] = useState(false);

  // Simulate real-time updates
  const startSimulation = useCallback(() => {
    setIsSimulating(true);
  }, []);

  const stopSimulation = useCallback(() => {
    setIsSimulating(false);
  }, []);

  useEffect(() => {
    if (!isSimulating) return;

    const interval = setInterval(() => {
      // Randomly update sensor data
      setSensorData(prev => prev.map(sensor => ({
        ...sensor,
        value: sensor.value + (Math.random() - 0.5) * 0.1,
        timestamp: new Date(),
      })));

      // Randomly add new timeline events
      if (Math.random() < 0.1) {
        const newEvent: TimelineEvent = {
          id: `evt-${Date.now()}`,
          timestamp: new Date(),
          type: Math.random() < 0.5 ? 'update' : 'alert',
          title: 'Status Update',
          description: 'New sensor data received from Zone ' + Math.floor(Math.random() * 4 + 1),
          severity: Math.random() < 0.3 ? 'critical' : 'info',
        };
        setTimelineEvents(prev => [newEvent, ...prev].slice(0, 20));
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isSimulating]);

  const executeRecommendation = useCallback((id: string) => {
    setRecommendations(prev => prev.map(rec => 
      rec.id === id ? { ...rec, status: 'executed' as const } : rec
    ));
  }, []);

  const dismissRecommendation = useCallback((id: string) => {
    setRecommendations(prev => prev.map(rec => 
      rec.id === id ? { ...rec, status: 'dismissed' as const } : rec
    ));
  }, []);

  const getZoneResources = useCallback((zoneId: string) => {
    return resources.filter(r => r.assignment === zoneId);
  }, [resources]);

  const getZoneRecommendations = useCallback((zoneId: string) => {
    return recommendations.filter(r => r.zoneId === zoneId);
  }, [recommendations]);

  return {
    zones,
    resources,
    recommendations,
    timelineEvents,
    sensorData,
    socialReports,
    incident,
    isSimulating,
    startSimulation,
    stopSimulation,
    executeRecommendation,
    dismissRecommendation,
    getZoneResources,
    getZoneRecommendations,
  };
}
