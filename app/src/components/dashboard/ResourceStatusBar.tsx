import { Ambulance, Users, Plane, Flame } from 'lucide-react';
import type { Resource } from '@/types';

interface ResourceStatusBarProps {
  resources: Resource[];
}

export function ResourceStatusBar({ resources }: ResourceStatusBarProps) {
  const getResourceStats = (type: Resource['type']) => {
    const ofType = resources.filter(r => r.type === type);
    const available = ofType.filter(r => r.status === 'available').length;
    const deployed = ofType.filter(r => r.status === 'deployed').length;
    const maintenance = ofType.filter(r => r.status === 'maintenance').length;
    return { total: ofType.length, available, deployed, maintenance };
  };

  const resourceTypes = [
    { type: 'ambulance' as const, icon: Ambulance, label: 'Ambulances', color: 'text-red-400' },
    { type: 'rescue_team' as const, icon: Users, label: 'Rescue Teams', color: 'text-blue-400' },
    { type: 'drone' as const, icon: Plane, label: 'Drones', color: 'text-cyan-400' },
    { type: 'fire_truck' as const, icon: Flame, label: 'Fire Units', color: 'text-orange-400' },
  ];

  return (
    <div className="bg-card border-b border-border px-6 py-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Resource Status
        </span>
        
        <div className="flex items-center gap-8">
          {resourceTypes.map(({ type, icon: Icon, label, color }) => {
            const stats = getResourceStats(type);
            return (
              <div key={type} className="flex items-center gap-3">
                <div className={`p-2 bg-muted rounded-lg ${color}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">{label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold text-foreground">
                      {stats.available}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      / {stats.total}
                    </span>
                    {stats.deployed > 0 && (
                      <span className="text-xs text-primary">
                        ({stats.deployed} deployed)
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
