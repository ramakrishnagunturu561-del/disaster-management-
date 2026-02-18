import { Shield, Bell, Clock, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { Incident } from '@/types';

interface HeaderProps {
  incident: Incident;
  isSimulating: boolean;
  onToggleSimulation: () => void;
}

export function Header({ incident, isSimulating, onToggleSimulation }: HeaderProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-500 animate-pulse';
      case 'contained': return 'bg-yellow-500';
      case 'resolved': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const formatDuration = (startDate: Date) => {
    const diff = Date.now() - startDate.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  return (
    <header className="bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">
                DISASTER DSS
              </h1>
              <p className="text-xs text-muted-foreground">
                AI-Driven Decision Support System
              </p>
            </div>
          </div>
          
          <div className="h-8 w-px bg-border mx-2" />
          
          {/* Incident Info */}
          <div className="flex items-center gap-3">
            <Badge 
              variant="outline" 
              className={`${getStatusColor(incident.status)} text-white border-0`}
            >
              {incident.status.toUpperCase()}
            </Badge>
            <div>
              <span className="text-sm font-medium text-foreground">
                {incident.type.toUpperCase()}
              </span>
              <span className="text-xs text-muted-foreground ml-2">
                Severity: {incident.severity}/10
              </span>
            </div>
          </div>
        </div>

        {/* Center: Duration */}
        <div className="flex items-center gap-2 bg-muted/50 px-4 py-2 rounded-lg">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Duration:</span>
          <span className="text-sm font-mono font-medium text-foreground">
            {formatDuration(incident.startedAt)}
          </span>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant={isSimulating ? 'default' : 'outline'}
            size="sm"
            onClick={onToggleSimulation}
            className="gap-2"
          >
            <Activity className={`w-4 h-4 ${isSimulating ? 'animate-pulse' : ''}`} />
            {isSimulating ? 'Stop Simulation' : 'Start Simulation'}
          </Button>
          
          <Button variant="outline" size="icon" className="relative">
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-destructive rounded-full text-[10px] flex items-center justify-center text-white">
              3
            </span>
          </Button>
        </div>
      </div>
    </header>
  );
}
