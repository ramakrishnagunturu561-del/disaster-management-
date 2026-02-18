import { 
  AlertTriangle, Activity, CheckCircle, Info,
  MapPin, Radio
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import type { TimelineEvent } from '@/types';

interface EmergencyTimelineProps {
  events: TimelineEvent[];
}

export function EmergencyTimeline({ events }: EmergencyTimelineProps) {
  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'incident': return AlertTriangle;
      case 'alert': return Radio;
      case 'action': return CheckCircle;
      case 'update': return Activity;
      default: return Info;
    }
  };

  const getSeverityColor = (severity: TimelineEvent['severity']) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-500/20';
      case 'warning': return 'text-yellow-500 bg-yellow-500/20';
      case 'info': return 'text-blue-500 bg-blue-500/20';
      default: return 'text-gray-500 bg-gray-500/20';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  const formatRelativeTime = (date: Date) => {
    const diff = Date.now() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <Card className="border-border h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          Real-Time Emergency Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          <div className="relative pl-6 pr-4 py-4">
            {/* Timeline line */}
            <div className="absolute left-8 top-4 bottom-4 w-px bg-border" />
            
            <div className="space-y-4">
              {events.map((event, index) => {
                const Icon = getEventIcon(event.type);
                const isLatest = index === 0;
                
                return (
                  <div 
                    key={event.id} 
                    className={`relative flex gap-4 ${isLatest ? 'animate-slide-in' : ''}`}
                  >
                    {/* Timeline dot */}
                    <div className={`absolute left-[-19px] z-10 w-6 h-6 rounded-full flex items-center justify-center ${getSeverityColor(event.severity)}`}>
                      <Icon className="w-3 h-3" />
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 ml-4">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-muted-foreground">
                          {formatTime(event.timestamp)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          ({formatRelativeTime(event.timestamp)})
                        </span>
                        {isLatest && (
                          <Badge variant="outline" className="text-[10px] h-4 border-primary text-primary">
                            NEW
                          </Badge>
                        )}
                      </div>
                      
                      <h4 className="text-sm font-medium text-foreground mt-1">
                        {event.title}
                      </h4>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {event.description}
                      </p>
                      
                      {event.zoneId && (
                        <div className="flex items-center gap-1 mt-1">
                          <MapPin className="w-3 h-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">
                            Zone: {event.zoneId}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
