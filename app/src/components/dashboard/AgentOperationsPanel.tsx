import React, { useState } from 'react';
import { Bot, Play, CheckCircle2, AlertTriangle, Clock, RefreshCw, Cpu, ShieldCheck } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface AgentStep {
  agent: string;
  action: string;
  status: string;
  timestamp: string;
  output_summary?: string;
  confidence?: number;
  errors?: string[];
}

export interface AgentOperationsPanelProps {
  agentState: Record<string, unknown> | null;
  isRunning: boolean;
  onRunWorkflow: () => void;
}

export const AgentOperationsPanel: React.FC<AgentOperationsPanelProps> = ({
  agentState,
  isRunning,
  onRunWorkflow,
}) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const history: AgentStep[] = (agentState?.agent_history as AgentStep[]) || [];
  const currentAgent = (agentState?.current_agent as string) || 'INCIDENT_COMMANDER';
  const replanCount = (agentState?.replan_count as number) || 0;
  const workflowStatus = (agentState?.workflow_status as string) || 'INITIALIZED';

  const agentsList = [
    { name: 'INCIDENT_COMMANDER', role: 'Supervisor & Classifier', icon: Cpu, color: 'text-purple-400' },
    { name: 'VISION_AGENT', role: 'YOLOv8 & OpenCV Damage Detection', icon: Bot, color: 'text-blue-400' },
    { name: 'EMERGENCY_INTELLIGENCE_AGENT', role: 'DistilBERT / NER NLP Engine', icon: Bot, color: 'text-green-400' },
    { name: 'WEATHER_AGENT', role: 'Open-Meteo Weather Intelligence', icon: Bot, color: 'text-cyan-400' },
    { name: 'SENSOR_AGENT', role: 'IoT Telemetry & Anomaly Analysis', icon: Bot, color: 'text-yellow-400' },
    { name: 'RISK_AGENT', role: 'Golden Hour & Priority Zone Scoring', icon: AlertTriangle, color: 'text-red-400' },
    { name: 'RESOURCE_AGENT', role: 'Constrained Resource Allocation Solver', icon: Bot, color: 'text-orange-400' },
    { name: 'ROUTE_AGENT', role: 'Geospatial Evacuation Corridor Router', icon: Bot, color: 'text-emerald-400' },
    { name: 'RESPONSE_PLANNER', role: 'Action Proposal Synthesizer', icon: Bot, color: 'text-indigo-400' },
    { name: 'CRITIC_AGENT', role: 'Safety Verification & Re-plan Guard', icon: ShieldCheck, color: 'text-rose-400' },
  ];

  return (
    <div className="space-y-4">
      {/* Top Banner & Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card p-4 rounded-xl border border-border">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              <Bot className="w-6 h-6 text-primary animate-pulse" />
              CrisisMind Agent Operations Center
            </h2>
            <Badge variant="secondary" className="text-xs bg-amber-500/10 text-amber-400 border-amber-500/20">
              SIMULATION MODE
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Real-time visual state machine & multi-agent execution pipeline trace
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="outline" className="gap-1 py-1">
            <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin text-primary' : ''}`} />
            Re-plan Count: {replanCount}
          </Badge>
          <Button 
            onClick={onRunWorkflow} 
            disabled={isRunning} 
            className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Agents Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run Multi-Agent Workflow
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Agent Nodes Status List */}
        <div className="lg:col-span-2 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {agentsList.map(agent => {
              const latestStep = [...history].reverse().find(s => s.agent === agent.name);
              const isActive = currentAgent === agent.name && isRunning;
              const isCompleted = latestStep?.status === 'COMPLETED';
              const isFailed = latestStep?.status === 'FAILED';

              return (
                <Card 
                  key={agent.name}
                  onClick={() => setSelectedAgent(agent.name)}
                  className={`cursor-pointer transition-all duration-200 border-border hover:border-primary/50 ${
                    isActive ? 'ring-2 ring-primary bg-primary/5' : ''
                  }`}
                >
                  <CardHeader className="p-3 pb-1 flex flex-row items-center justify-between">
                    <div className="flex items-center gap-2">
                      <agent.icon className={`w-4 h-4 ${agent.color}`} />
                      <CardTitle className="text-xs font-bold text-foreground">
                        {agent.name.replace(/_/g, ' ')}
                      </CardTitle>
                    </div>
                    {isActive ? (
                      <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-[10px] animate-pulse">
                        RUNNING
                      </Badge>
                    ) : isCompleted ? (
                      <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-[10px]">
                        COMPLETED
                      </Badge>
                    ) : isFailed ? (
                      <Badge className="bg-red-500/20 text-red-400 border-red-500/30 text-[10px]">
                        FAILED
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] text-muted-foreground">
                        IDLE
                      </Badge>
                    )}
                  </CardHeader>
                  <CardContent className="p-3 pt-1 space-y-2">
                    <p className="text-[11px] text-muted-foreground">{agent.role}</p>
                    {latestStep ? (
                      <div className="space-y-1">
                        <p className="text-xs text-foreground line-clamp-2 font-medium">
                          {latestStep.output_summary}
                        </p>
                        {latestStep.confidence !== undefined && (
                          <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                            <span>Confidence Score</span>
                            <span className="font-bold text-primary">{(latestStep.confidence * 100).toFixed(0)}%</span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-xs italic text-muted-foreground">Awaiting workflow trigger...</p>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Live Trace Audit Stream */}
        <div className="space-y-3">
          <Card className="border-border h-full flex flex-col">
            <CardHeader className="pb-2 border-b border-border">
              <CardTitle className="text-sm font-bold text-foreground flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-primary" />
                  Agent Execution Log
                </span>
                <Badge variant="outline" className="text-[10px]">
                  {history.length} Steps Recorded
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-3 flex-1 overflow-y-auto max-h-[580px] space-y-3">
              {history.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground text-xs">
                  No agent steps recorded yet.<br />
                  Click "Run Multi-Agent Workflow" above to start execution.
                </div>
              ) : (
                history.map((step, idx) => (
                  <div key={idx} className="p-2.5 bg-muted/50 rounded-lg border border-border/50 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-primary font-mono text-[11px]">{step.agent}</span>
                      <span className="text-[10px] text-muted-foreground font-mono">
                        {new Date(step.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-foreground font-medium text-xs">{step.action}</p>
                    <p className="text-muted-foreground text-[11px] leading-relaxed">{step.output_summary}</p>
                    {step.confidence !== undefined && (
                      <div className="flex items-center gap-1 text-[10px] text-emerald-400 pt-0.5">
                        <CheckCircle2 className="w-3 h-3" />
                        Confidence: {(step.confidence * 100).toFixed(0)}%
                      </div>
                    )}
                    {step.errors && step.errors.length > 0 && (
                      <div className="p-1.5 bg-red-500/10 rounded border border-red-500/20 text-red-400 text-[10px] space-y-0.5">
                        {step.errors.map((err, i) => (
                          <div key={i}>⚠️ {err}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
