import React, { useState } from 'react';
import { Activity, MapPin, FileText, Upload, Shield, Play, RefreshCw, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

export interface LiveIntelligenceFormProps {
  onRunLiveAnalysis: (data: Record<string, unknown>) => void;
  isRunning: boolean;
}

export const LiveIntelligenceForm: React.FC<LiveIntelligenceFormProps> = ({ onRunLiveAnalysis, isRunning }) => {
  const [title, setTitle] = useState('Urban Flood & Infrastructure Emergency');
  const [incidentType, setIncidentType] = useState('flood');
  const [latitude, setLatitude] = useState(16.5062);
  const [longitude, setLongitude] = useState(80.6480);
  const [emergencyText, setEmergencyText] = useState('Water rising rapidly near residential sectors. Damaged bridge corridor reported on highway.');
  const [rescueTeams, setRescueTeams] = useState(6);
  const [ambulances, setAmbulances] = useState(10);
  const [rescueBoats, setRescueBoats] = useState(4);

  const presets = [
    { name: 'Vijayawada Flood', lat: 16.5062, lon: 80.6480, type: 'flood' },
    { name: 'Visakhapatnam Cyclone', lat: 17.6868, lon: 83.2185, type: 'cyclone' },
    { name: 'Chennai Coastal Storm', lat: 13.0827, lon: 80.2707, type: 'flood' },
    { name: 'Mumbai Monsoon Alert', lat: 19.0760, lon: 72.8777, type: 'flood' },
    { name: 'Hyderabad Urban Inundation', lat: 17.3850, lon: 78.4867, type: 'flood' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onRunLiveAnalysis({
      title,
      incident_type: incidentType,
      latitude,
      longitude,
      emergency_text: emergencyText,
      available_resources: {
        rescue_teams: rescueTeams,
        ambulances: ambulances,
        rescue_boats: rescueBoats,
        drones: 4
      }
    });
  };

  return (
    <Card className="border-primary/30 bg-card">
      <CardHeader className="py-3 px-4 border-b border-border">
        <CardTitle className="text-sm font-bold flex items-center justify-between">
          <span className="flex items-center gap-2 text-foreground">
            <Activity className="w-4 h-4 text-emerald-400 animate-pulse" />
            LIVE INTELLIGENCE MODE — Real Location Dispatch & Multi-Agent Analysis
          </span>
          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs font-mono">
            OPEN-METEO & YOLOV8 LIVE CONNECTED
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Presets */}
          <div className="space-y-1.5">
            <label className="font-bold text-muted-foreground text-[11px] block">Quick Location Presets:</label>
            <div className="flex flex-wrap gap-2">
              {presets.map((p, idx) => (
                <Button
                  key={idx}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setTitle(p.name);
                    setLatitude(p.lat);
                    setLongitude(p.lon);
                    setIncidentType(p.type);
                  }}
                  className="text-[11px] py-1 h-auto border-border hover:border-primary"
                >
                  <MapPin className="w-3 h-3 mr-1 text-primary" />
                  {p.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1">
              <label className="font-bold text-foreground">Incident Title</label>
              <Input
                value={title}
                onChange={e => setTitle(e.target.value)}
                className="bg-background text-xs"
              />
            </div>
            <div className="space-y-1">
              <label className="font-bold text-foreground">Latitude</label>
              <Input
                type="number"
                step="0.0001"
                value={latitude}
                onChange={e => setLatitude(parseFloat(e.target.value))}
                className="bg-background text-xs font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="font-bold text-foreground">Longitude</label>
              <Input
                type="number"
                step="0.0001"
                value={longitude}
                onChange={e => setLongitude(parseFloat(e.target.value))}
                className="bg-background text-xs font-mono"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="font-bold text-foreground flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-primary" />
              Live Emergency Text Report (DistilBERT / BERT NLP Engine Ingest)
            </label>
            <Textarea
              value={emergencyText}
              onChange={e => setEmergencyText(e.target.value)}
              rows={2}
              className="bg-background text-xs"
              placeholder="Enter live field reports or 911 calls..."
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <label className="font-bold text-foreground text-[11px]">Rescue Teams</label>
              <Input
                type="number"
                value={rescueTeams}
                onChange={e => setRescueTeams(parseInt(e.target.value) || 0)}
                className="bg-background text-xs font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="font-bold text-foreground text-[11px]">Ambulances</label>
              <Input
                type="number"
                value={ambulances}
                onChange={e => setAmbulances(parseInt(e.target.value) || 0)}
                className="bg-background text-xs font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="font-bold text-foreground text-[11px]">Rescue Boats</label>
              <Input
                type="number"
                value={rescueBoats}
                onChange={e => setRescueBoats(parseInt(e.target.value) || 0)}
                className="bg-background text-xs font-mono"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={isRunning}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold gap-2 text-xs"
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running Live Agents...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  RUN LIVE CRISIS ANALYSIS
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
