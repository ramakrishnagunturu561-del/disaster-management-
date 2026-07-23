import React, { useState } from 'react';
import { Bot, Play, CheckCircle2, AlertTriangle, Clock, RefreshCw, Cpu, ShieldCheck, ArrowRight, Activity, FileText, Database } from 'lucide-react';
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
  const criticResult = agentState?.critic_result as Record<string, unknown> | undefined;
  const decisionVersion = (agentState?.decision_version as number) || 1;

  const agentsList = [
    { name: 'INCIDENT_COMMANDER', role: 'Supervisor & Classifier', icon: Cpu, color: 'text-purple-400', provenance: 'DERIVED' },
    { name: 'VISION_AGENT', role: 'YOLOv8 & OpenCV Damage Detection', icon: Bot, color: 'text-blue-400', provenance: 'REAL' },
    { name: 'EMERGENCY_INTELLIGENCE_AGENT', role: 'DistilBERT / NER NLP Engine', icon: Bot, color: 'text-green-400', provenance: 'REAL' },
    { name: 'WEATHER_AGENT', role: 'Open-Meteo Weather Intelligence', icon: Bot, color: 'text-cyan-400', provenance: 'REAL' },
    { name: 'SENSOR_AGENT', role: 'IoT Telemetry & Anomaly Analysis', icon: Bot, color: 'text-yellow-400', provenance: 'SIMULATED' },
    { name: 'RISK_AGENT', role: 'Golden Hour & Priority Zone Scoring', icon: AlertTriangle, color: 'text-red-400', provenance: 'DERIVED' },
    { name: 'RESOURCE_AGENT', role: 'Constrained Resource Allocation Solver', icon: Bot, color: 'text-orange-400', provenance: 'DERIVED' },
    { name: 'ROUTE_AGENT', role: 'Geospatial Evacuation Corridor Router', icon: Bot, color: 'text-emerald-400', provenance: 'DERIVED' },
    { name: 'RESPONSE_PLANNER', role: 'Action Proposal Synthesizer', icon: Bot, color: 'text-indigo-400', provenance: 'DERIVED' },
    { name: 'CRITIC_AGENT', role: 'Safety Verification & Re-plan Guard', icon: ShieldCheck, color: 'text-rose-400', provenance: 'DERIVED' },
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
          <Badge variant="outline" className="gap-1 py-1 text-xs font-mono">
            Decision Version: v{decisionVersion}
          </Badge>
          <Badge variant="outline" className="gap-1 py-1 text-xs">
            <RefreshCw className={`w-3.5 h-3.5 ${replanCount > 0 ? 'animate-spin text-amber-400' : ''}`} />
            Re-plan Count: {replanCount}/3
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

      {/* LangGraph State Machine Architecture Pipeline Diagram */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader className="py-3">
          <CardTitle className="text-sm font-bold flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              LangGraph StateGraph Pipeline Workflow
            </span>
            <Badge className={
              workflowStatus === 'HUMAN_REVIEW_REQUIRED' ? 'bg-red-500/20 text-red-400' :
              workflowStatus === 'AWAITING_HUMAN_APPROVAL' ? 'bg-emerald-500/20 text-emerald-400' :
              workflowStatus === 'RUNNING' ? 'bg-primary/20 text-primary' : 'bg-secondary text-secondary-foreground'
            }>
              STATUS: {workflowStatus}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pb-4">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-medium pt-2">
            <div className="flex items-center gap-1.5 px-3 py-2 bg-purple-500/10 border border-purple-500/30 rounded-lg text-purple-300">
              <span>START</span>
              <ArrowRight className="w-3.5 h-3.5" />
              <span>SUPERVISOR</span>
            </div>

            <ArrowRight className="w-4 h-4 text-muted-foreground hidden sm:inline" />

            <div className="flex flex-col gap-1 p-2 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-300">
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Parallel Intelligence</span>
              <span>Vision • NLP • Weather • Sensors</span>
            </div>

            <ArrowRight className="w-4 h-4 text-muted-foreground hidden sm:inline" />

            <div className="px-3 py-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300">
              <span>RISK AGENT</span>
            </div>

            <ArrowRight className="w-4 h-4 text-muted-foreground hidden sm:inline" />

            <div className="flex flex-col gap-1 p-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-300">
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Parallel Planning</span>
              <span>Resource Solver • Route Router</span>
            </div>

            <ArrowRight className="w-4 h-4 text-muted-foreground hidden sm:inline" />

            <div className="px-3 py-2 bg-indigo-500/10 border border-indigo-500/30 rounded-lg text-indigo-300">
              <span>RESPONSE PLANNER</span>
            </div>

            <ArrowRight className="w-4 h-4 text-muted-foreground hidden sm:inline" />

            <div className="px-3 py-2 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>CRITIC</span>
            </div>
          </div>
        </CardContent>
      </Card>

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
              const isReplanning = replanCount > 0 && ['RESOURCE_AGENT', 'ROUTE_AGENT', 'RESPONSE_PLANNER'].includes(agent.name);

              const Icon = agent.icon;

              return (
                <Card 
                  key={agent.name}
                  onClick={() => setSelectedAgent(agent.name)}
                  className={`cursor-pointer transition-all duration-200 hover:border-primary/50 ${
                    isActive ? 'border-primary ring-2 ring-primary/20 bg-primary/5' : 
                    selectedAgent === agent.name ? 'border-primary/50 bg-secondary/30' : 'bg-card'
                  }`}
                >
                  <CardContent className="p-3.5">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <div className={`p-2 rounded-lg bg-secondary ${agent.color}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-foreground truncate max-w-[140px]">
                            {agent.name.replace('_AGENT', '').replace('_', ' ')}
                          </h4>
                          <p className="text-[10px] text-muted-foreground truncate max-w-[160px]">
                            {agent.role}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-col items-end gap-1">
                        {isActive ? (
                          <Badge className="bg-primary/20 text-primary border-primary/30 text-[10px] gap-1 py-0.5 animate-pulse">
                            <Clock className="w-2.5 h-2.5 animate-spin" /> RUNNING
                          </Badge>
                        ) : isReplanning ? (
                          <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-[10px] gap-1 py-0.5">
                            <RefreshCw className="w-2.5 h-2.5 animate-spin" /> REPLANNING
                          </Badge>
                        ) : isCompleted ? (
                          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] gap-1 py-0.5">
                            <CheckCircle2 className="w-2.5 h-2.5" /> DONE
                          </Badge>
                        ) : isFailed ? (
                          <Badge className="bg-red-500/10 text-red-400 border-red-500/20 text-[10px] gap-1 py-0.5">
                            <AlertTriangle className="w-2.5 h-2.5" /> FAIL
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-[10px] py-0.5 text-muted-foreground">
                            IDLE
                          </Badge>
                        )}

                        <Badge variant="secondary" className="text-[9px] px-1 py-0 font-mono">
                          {agent.provenance}
                        </Badge>
                      </div>
                    </div>

                    {latestStep && (
                      <div className="mt-2.5 pt-2 border-t border-border/50 flex items-center justify-between text-[11px] text-muted-foreground">
                        <span className="truncate max-w-[190px]">
                          {latestStep.output_summary || latestStep.action}
                        </span>
                        {latestStep.confidence !== undefined && (
                          <span className="font-mono text-xs text-foreground font-semibold">
                            {Math.round(latestStep.confidence * 100)}%
                          </span>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Execution Log & Step Details Inspector */}
        <div className="space-y-3">
          <Card className="h-[440px] flex flex-col bg-card">
            <CardHeader className="py-3 px-4 border-b border-border">
              <CardTitle className="text-xs font-bold flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-foreground">
                  <FileText className="w-4 h-4 text-primary" />
                  Agent Execution Log ({history.length} Steps)
                </span>
                {replanCount > 0 && (
                  <Badge variant="outline" className="text-[10px] text-amber-400 border-amber-500/30">
                    Self-Corrected x{replanCount}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-3 flex-1 overflow-y-auto space-y-2 font-mono text-[11px]">
              {history.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-muted-foreground text-center p-4">
                  <Bot className="w-8 h-8 text-muted-foreground/30 mb-2" />
                  <p className="text-xs">No execution trace recorded.</p>
                  <p className="text-[10px]">Click 'Run Multi-Agent Workflow' to initiate agents.</p>
                </div>
              ) : (
                history.map((step, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-secondary/40 border border-border/50 space-y-1">
                    <div className="flex items-center justify-between text-muted-foreground text-[10px]">
                      <span className="font-bold text-primary">{step.agent}</span>
                      <span>{new Date(step.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-foreground text-xs font-sans font-medium">
                      {step.output_summary || step.action}
                    </p>
                    {step.errors && step.errors.length > 0 && (
                      <div className="text-red-400 text-[10px] bg-red-500/10 p-1.5 rounded border border-red-500/20">
                        {step.errors.join(' | ')}
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
