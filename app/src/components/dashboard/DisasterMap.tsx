import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Zone, Resource, Incident } from '@/types';

// Fix Leaflet default icons
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface DisasterMapProps {
  zones: Zone[];
  resources: Resource[];
  incident: Incident;
  selectedZone: string | null;
  onZoneSelect: (zoneId: string) => void;
}

export function DisasterMap({ zones, resources, incident, selectedZone, onZoneSelect }: DisasterMapProps) {
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const zonesLayerRef = useRef<L.LayerGroup | null>(null);
  const resourcesLayerRef = useRef<L.LayerGroup | null>(null);

  const getRiskColor = (riskLevel: Zone['riskLevel']) => {
    switch (riskLevel) {
      case 'critical': return '#ef4444';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const getResourceIcon = (type: Resource['type']) => {
    const colors = {
      ambulance: '#ef4444',
      rescue_team: '#3b82f6',
      drone: '#06b6d4',
      fire_truck: '#f97316',
    };
    
    return L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="
        width: 12px;
        height: 12px;
        background: ${colors[type]};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 0 8px ${colors[type]};
      "></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    });
  };

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Initialize map
    const map = L.map(mapContainerRef.current, {
      center: incident.location,
      zoom: 14,
      zoomControl: false,
      attributionControl: false,
    });

    // Add dark tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
    }).addTo(map);

    // Add zoom control to bottom right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    mapRef.current = map;
    zonesLayerRef.current = L.layerGroup().addTo(map);
    resourcesLayerRef.current = L.layerGroup().addTo(map);

    // Add incident marker
    const incidentIcon = L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="
        width: 20px;
        height: 20px;
        background: radial-gradient(circle, #ef4444 0%, transparent 70%);
        border-radius: 50%;
        animation: pulse 2s infinite;
      "></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });

    L.marker(incident.location, { icon: incidentIcon })
      .addTo(map)
      .bindPopup(`<b>${incident.type.toUpperCase()}</b><br/>Magnitude: ${incident.severity}/10`);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [incident]);

  // Update zones
  useEffect(() => {
    if (!mapRef.current || !zonesLayerRef.current) return;

    zonesLayerRef.current.clearLayers();

    zones.forEach(zone => {
      const polygon = L.polygon(zone.coordinates, {
        color: getRiskColor(zone.riskLevel),
        fillColor: getRiskColor(zone.riskLevel),
        fillOpacity: selectedZone === zone.id ? 0.5 : 0.2,
        weight: selectedZone === zone.id ? 3 : 2,
      }).addTo(zonesLayerRef.current!);

      polygon.bindPopup(`
        <div style="color: #1f2937;">
          <b>${zone.name}</b><br/>
          Risk Level: ${zone.riskLevel.toUpperCase()}<br/>
          Damage: ${zone.damageScore}%<br/>
          Survival: ${zone.survivalProbability}%<br/>
          Population: ${zone.population.toLocaleString()}
        </div>
      `);

      polygon.on('click', () => onZoneSelect(zone.id));
    });
  }, [zones, selectedZone, onZoneSelect]);

  // Update resources
  useEffect(() => {
    if (!mapRef.current || !resourcesLayerRef.current) return;

    resourcesLayerRef.current.clearLayers();

    resources.forEach(resource => {
      if (resource.location) {
        L.marker(resource.location, { icon: getResourceIcon(resource.type) })
          .addTo(resourcesLayerRef.current!)
          .bindPopup(`
            <div style="color: #1f2937;">
              <b>${resource.type.replace('_', ' ').toUpperCase()}</b><br/>
              Status: ${resource.status}<br/>
              ${resource.assignment ? `Assigned to: ${resource.assignment}` : 'Unassigned'}
            </div>
          `);
      }
    });
  }, [resources]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainerRef} className="w-full h-full rounded-lg" />
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-card/90 backdrop-blur-sm p-3 rounded-lg border border-border z-[1000]">
        <h4 className="text-xs font-medium text-muted-foreground mb-2">Zone Risk Levels</h4>
        <div className="space-y-1">
          {[
            { level: 'critical', color: '#ef4444', label: 'Critical' },
            { level: 'high', color: '#f97316', label: 'High' },
            { level: 'medium', color: '#eab308', label: 'Medium' },
            { level: 'low', color: '#22c55e', label: 'Low' },
          ].map(({ color, label }) => (
            <div key={label} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-sm" 
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-foreground">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
