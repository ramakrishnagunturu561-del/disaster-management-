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
              <h1 className="text-xl font-bold text-foreground tracking-wide">
                CRISISMIND AI
              </h1>
              <p className="text-[11px] text-muted-foreground font-medium">
                Agentic Emergency Operations Command Center
              </p>
            </div>
          </div>
          
          <div className="h-8 w-px bg-border mx-2" />
          
          {/* System Mode & Incident Info */}
          <div className="flex items-center gap-2">
            <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 text-xs font-mono">
              SIMULATION MODE
            </Badge>
            <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs font-mono">
              SYSTEM: OPERATIONAL
            </Badge>
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
