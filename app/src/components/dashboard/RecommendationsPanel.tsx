import { useState } from 'react';
import { 
  Users, Plane, Ambulance, AlertTriangle, 
  CheckCircle, XCircle, ChevronDown, ChevronUp,
  Brain
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { Recommendation } from '@/types';

interface RecommendationsPanelProps {
  recommendations: Recommendation[];
  onExecute: (id: string) => void;
  onDismiss: (id: string) => void;
}

export function RecommendationsPanel({ recommendations, onExecute, onDismiss }: RecommendationsPanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const getCategoryIcon = (category: Recommendation['category']) => {
    switch (category) {
      case 'rescue': return Users;
      case 'evacuation': return AlertTriangle;
      case 'surveillance': return Plane;
      case 'medical': return Ambulance;
      default: return CheckCircle;
    }
  };

  const getPriorityColor = (priority: Recommendation['priority']) => {
    switch (priority) {
      case 'critical': return 'bg-red-500/20 text-red-500 border-red-500/50';
      case 'high': return 'bg-orange-500/20 text-orange-500 border-orange-500/50';
      case 'medium': return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50';
      case 'low': return 'bg-green-500/20 text-green-500 border-green-500/50';
    }
  };

  const pendingRecommendations = recommendations.filter(r => r.status === 'pending');
  const executedRecommendations = recommendations.filter(r => r.status === 'executed');

  const formatTime = (date: Date) => {
    const diff = Date.now() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="border-border">
          <CardContent className="p-3">
            <p className="text-xs text-muted-foreground">Pending</p>
            <p className="text-xl font-bold text-foreground">{pendingRecommendations.length}</p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-3">
            <p className="text-xs text-muted-foreground">Executed</p>
            <p className="text-xl font-bold text-green-500">{executedRecommendations.length}</p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-3">
            <p className="text-xs text-muted-foreground">Critical</p>
            <p className="text-xl font-bold text-red-500">
              {pendingRecommendations.filter(r => r.priority === 'critical').length}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Pending Recommendations */}
      <Card className="border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Brain className="w-4 h-4 text-primary" />
            AI Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[300px]">
            <div className="divide-y divide-border">
              {pendingRecommendations.length === 0 ? (
                <div className="px-4 py-8 text-center">
                  <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">All recommendations executed</p>
                </div>
              ) : (
                pendingRecommendations.map(rec => {
                  const Icon = getCategoryIcon(rec.category);
                  const isExpanded = expandedId === rec.id;
                  
                  return (
                    <div key={rec.id} className="p-4">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${getPriorityColor(rec.priority)}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-medium text-foreground truncate">
                              {rec.title}
                            </h4>
                            <Badge variant="outline" className={`text-xs ${getPriorityColor(rec.priority)}`}>
                              {rec.priority}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {rec.description}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatTime(rec.timestamp)}
                          </p>
                          
                          {/* Expandable reasoning */}
                          {isExpanded && (
                            <div className="mt-3 p-3 bg-muted rounded-lg animate-fade-in">
                              <p className="text-xs font-medium text-foreground mb-1">
                                <Brain className="w-3 h-3 inline mr-1" />
                                AI Reasoning:
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {rec.reasoning}
                              </p>
                            </div>
                          )}
                          
                          <div className="flex items-center gap-2 mt-3">
                            <Button 
                              size="sm" 
                              className="h-7 text-xs"
                              onClick={() => onExecute(rec.id)}
                            >
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Execute
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline"
                              className="h-7 text-xs"
                              onClick={() => onDismiss(rec.id)}
                            >
                              <XCircle className="w-3 h-3 mr-1" />
                              Dismiss
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="h-7 text-xs"
                              onClick={() => setExpandedId(isExpanded ? null : rec.id)}
                            >
                              {isExpanded ? (
                                <><ChevronUp className="w-3 h-3 mr-1" /> Less</>
                              ) : (
                                <><ChevronDown className="w-3 h-3 mr-1" /> Why?</>
                              )}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Executed Recommendations */}
      {executedRecommendations.length > 0 && (
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Executed Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[150px]">
              <div className="divide-y divide-border">
                {executedRecommendations.map(rec => {
                  const Icon = getCategoryIcon(rec.category);
                  
                  return (
                    <div key={rec.id} className="px-4 py-3 flex items-center gap-3 opacity-60">
                      <div className="p-2 rounded-lg bg-green-500/20 text-green-500">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-foreground line-through">
                          {rec.title}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          Executed {formatTime(rec.timestamp)}
                        </p>
                      </div>
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
