import { useState, useEffect, useCallback } from 'react';
import { api, WebSocketClient, type Zone, type Resource, type Recommendation, type TimelineEvent, type DashboardStats } from '@/services/api';

export function useApiDashboard() {
  const [zones, setZones] = useState<Zone[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsClient] = useState(() => new WebSocketClient());

  // Load initial data
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [zonesData, resourcesData, recommendationsData, statsData] = await Promise.all([
        api.getZones(),
        api.getResources(),
        api.getRecommendations(),
        api.getDashboardStats(),
      ]);
      
      setZones(zonesData);
      setResources(resourcesData);
      setRecommendations(recommendationsData);
      setStats(statsData);
      
      // Load timeline for first active incident
      const incidents = await api.getIncidents('active');
      if (incidents.length > 0) {
        const timeline = await api.getTimeline(incidents[0].id);
        setTimelineEvents(timeline);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Execute recommendation
  const executeRecommendation = useCallback(async (id: string) => {
    try {
      await api.executeRecommendation(id, 'operator');
      setRecommendations(prev => prev.map(rec => 
        rec.id === id ? { ...rec, status: 'executed' as const } : rec
      ));
    } catch (err) {
      console.error('Failed to execute recommendation:', err);
    }
  }, []);

  // Dismiss recommendation
  const dismissRecommendation = useCallback(async (id: string) => {
    // Note: Backend doesn't have dismiss endpoint, we'll just filter locally
    setRecommendations(prev => prev.map(rec => 
      rec.id === id ? { ...rec, status: 'dismissed' as const } : rec
    ));
  }, []);

  // Generate recommendations for a zone
  const generateRecommendations = useCallback(async (zoneId: string) => {
    try {
      const result = await api.generateRecommendations(zoneId);
      setRecommendations(prev => [...result.recommendations, ...prev]);
    } catch (err) {
      console.error('Failed to generate recommendations:', err);
    }
  }, []);

  // Assign resource to zone
  const assignResource = useCallback(async (resourceId: string, zoneId: string) => {
    try {
      await api.assignResource(resourceId, zoneId);
      setResources(prev => prev.map(r => 
        r.id === resourceId ? { ...r, zone_id: zoneId, status: 'deployed' as const } : r
      ));
    } catch (err) {
      console.error('Failed to assign resource:', err);
    }
  }, []);

  // Get zone resources
  const getZoneResources = useCallback((zoneId: string) => {
    return resources.filter(r => r.zone_id === zoneId);
  }, [resources]);

  // Get zone recommendations
  const getZoneRecommendations = useCallback((zoneId: string) => {
    return recommendations.filter(r => r.zone_id === zoneId);
  }, [recommendations]);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Setup WebSocket for real-time updates
  useEffect(() => {
    wsClient.connect();
    
    wsClient.onMessage((data) => {
      if (data.type === 'update') {
        // Refresh data on update
        loadData();
      }
    });
    
    return () => {
      wsClient.disconnect();
    };
  }, [wsClient, loadData]);

  return {
    zones,
    resources,
    recommendations,
    timelineEvents,
    stats,
    isLoading,
    error,
    refreshData: loadData,
    executeRecommendation,
    dismissRecommendation,
    generateRecommendations,
    assignResource,
    getZoneResources,
    getZoneRecommendations,
  };
}
