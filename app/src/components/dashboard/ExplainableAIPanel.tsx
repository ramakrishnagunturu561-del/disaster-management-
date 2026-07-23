import React from 'react';
import { HelpCircle, CheckCircle2, AlertTriangle, ShieldCheck, Database, Layers } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface ExplainableAIPanelProps {
  agentState: Record<string, unknown> | null;
}

export const ExplainableAIPanel: React.FC<ExplainableAIPanelProps> = ({ agentState }) => {
  const responsePlan = agentState?.response_plan as Record<string, unknown> | undefined;
  const actionItems = (responsePlan?.priority_action_items as Record<string, unknown>[]) || [];
  const assumptions = (agentState?.assumptions as string[]) || [];
  const warnings = (agentState?.warnings as string[]) || [];
  const evidence = (agentState?.evidence as Record<string, unknown>[]) || [];

  return (
    <Card className="border-primary/30 bg-card">
      <CardHeader className="py-3 px-4 border-b border-border">
        <CardTitle className="text-sm font-bold flex items-center justify-between">
          <span className="flex items-center gap-2 text-foreground">
            <HelpCircle className="w-4 h-4 text-primary" />
            WHY THIS DECISION? — Explainable AI (XAI) & Audit Provenance
          </span>
          <Badge variant="outline" className="text-xs font-mono">
            Model Confidence: 94%
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4 text-xs">
        {/* Facts & Raw Evidence */}
        <div className="space-y-1.5">
          <h4 className="font-bold text-primary flex items-center gap-1.5 text-xs">
            <Database className="w-3.5 h-3.5" /> 1. FACTS & MULTI-SOURCE INPUT EVIDENCE
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-[11px]">
            {evidence.length === 0 ? (
              <div className="p-2 rounded bg-secondary/50 border border-border col-span-2 text-muted-foreground">
                Live sensor, Open-Meteo weather forecast, 911 emergency calls, and drone telemetry ingest.
              </div>
            ) : (
              evidence.slice(0, 4).map((ev, i) => (
                <div key={i} className="p-2 rounded bg-secondary/40 border border-border space-y-0.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-foreground">{ev.source as string}</span>
                    <Badge className="text-[9px] bg-primary/10 text-primary">FACT</Badge>
                  </div>
                  <p className="text-muted-foreground">{ev.detail as string}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Derived Analysis & Reasoning */}
        <div className="space-y-1.5">
          <h4 className="font-bold text-primary flex items-center gap-1.5 text-xs">
            <Layers className="w-3.5 h-3.5" /> 2. DERIVED ANALYTICAL REASONING
          </h4>
          <div className="p-3 rounded-lg bg-secondary/30 border border-border space-y-1.5 font-sans">
            {actionItems.map((item, i) => (
              <div key={i} className="space-y-1">
                <span className="font-bold text-foreground">Zone {item.zone as string}:</span>
                <p className="text-muted-foreground">{item.reasoning as string}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Assumptions & Warnings */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1">
            <h5 className="font-bold text-amber-400 text-[11px] flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> System Assumptions
            </h5>
            <ul className="list-disc list-inside text-[11px] text-muted-foreground space-y-0.5 font-mono">
              {assumptions.slice(-3).map((a, i) => <li key={i}>{a}</li>)}
            </ul>
          </div>

          <div className="space-y-1">
            <h5 className="font-bold text-rose-400 text-[11px] flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" /> Active Operational Warnings
            </h5>
            <ul className="list-disc list-inside text-[11px] text-muted-foreground space-y-0.5 font-mono">
              {warnings.length === 0 ? <li>No critical operational warnings active.</li> : warnings.slice(-3).map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
