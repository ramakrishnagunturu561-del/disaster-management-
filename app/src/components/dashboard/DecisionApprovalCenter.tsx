import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, Edit3, AlertOctagon, HelpCircle, FileText, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';

export interface DecisionApprovalCenterProps {
  agentState: Record<string, unknown> | null;
  onApprove: () => void;
  onReject: (reason: string) => void;
  onModify: (modifications: Record<string, unknown>) => void;
}

export const DecisionApprovalCenter: React.FC<DecisionApprovalCenterProps> = ({
  agentState,
  onApprove,
  onReject,
  onModify,
}) => {
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectBox, setShowRejectBox] = useState(false);
  const [explainModalOpen, setExplainModalOpen] = useState(false);

  const responsePlan = agentState?.response_plan as Record<string, unknown> | undefined;
  const criticResult = agentState?.critic_result as Record<string, unknown> | undefined;
  const approvalStatus = (agentState?.approval_status as string) || 'PROPOSED';
  const executionStatus = (agentState?.execution_status as string) || 'PENDING';
  const priorityZones = (agentState?.priority_zones as Record<string, unknown>[]) || [];
  const actionItems = (responsePlan?.priority_action_items as Record<string, unknown>[]) || [];

  const criticPassed = criticResult?.passed === true;

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card p-4 rounded-xl border border-border">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
              Decision Approval Center
            </h2>
            <Badge className={
              approvalStatus === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
              approvalStatus === 'REJECTED' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
              'bg-amber-500/20 text-amber-400 border-amber-500/30'
            }>
              STATUS: {approvalStatus}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Human-in-the-Loop Operational Plan Authorization & Command Governance
          </p>
        </div>

        {/* Commander Approval Action Buttons */}
        <div className="flex items-center gap-2">
          {approvalStatus === 'APPROVED' ? (
            <Badge className="px-4 py-2 bg-emerald-500/20 text-emerald-400 border-emerald-500/40 text-xs font-bold gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              PLAN APPROVED — EXECUTED (SIMULATED)
            </Badge>
          ) : (
            <>
              <Button 
                onClick={onApprove}
                disabled={!responsePlan || !criticPassed}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" />
                APPROVE PLAN
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowRejectBox(!showRejectBox)}
                disabled={!responsePlan}
                className="border-red-500/40 text-red-400 hover:bg-red-500/10 gap-1.5"
              >
                <XCircle className="w-4 h-4" />
                REJECT / REVISE
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Reject Reason Box */}
      {showRejectBox && (
        <Card className="border-red-500/30 bg-red-500/5">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-xs font-bold text-red-400 flex items-center gap-1.5">
              <AlertOctagon className="w-4 h-4" />
              Provide Reason for Rejection / Revision Request
            </h4>
            <Textarea
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
              placeholder="e.g. Commander requests allocation of additional rescue boats to Zone C..."
              className="bg-background text-xs border-border"
            />
            <div className="flex justify-end gap-2">
              <Button size="sm" variant="ghost" onClick={() => setShowRejectBox(false)}>Cancel</Button>
              <Button 
                size="sm" 
                className="bg-red-600 hover:bg-red-500 text-white"
                onClick={() => {
                  onReject(rejectReason || 'Commander requested revision');
                  setShowRejectBox(false);
                }}
              >
                Confirm Rejection
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: Proposed Action Plan */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <CardTitle className="text-base font-bold text-foreground flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                AI Generated Response Proposal
              </CardTitle>
              {criticResult && (
                <Badge className={criticPassed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}>
                  SAFETY CRITIC: {criticPassed ? 'PASS' : 'FAIL'}
                </Badge>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              {responsePlan ? (
                <>
                  <div className="p-3 bg-muted rounded-lg text-xs leading-relaxed text-foreground border border-border/60">
                    <p className="font-semibold text-primary mb-1">Executive Summary:</p>
                    {responsePlan.executive_summary as string}
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Prioritized Operational Directives ({actionItems.length} Blocks)
                    </h4>

                    {actionItems.map((item, idx) => (
                      <div key={idx} className="p-4 bg-card rounded-lg border border-border space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge className="bg-primary text-primary-foreground font-mono font-bold text-xs">
                              PRIORITY #{item.priority as number}
                            </Badge>
                            <span className="font-bold text-foreground text-sm">{item.zone as string}</span>
                          </div>
                          <Badge variant="outline" className="border-red-500/40 text-red-400 text-xs">
                            {item.risk_category as string} THREAT
                          </Badge>
                        </div>

                        <div className="space-y-1.5 text-xs text-foreground">
                          <p className="font-semibold text-muted-foreground">Tactical Actions:</p>
                          <ul className="list-disc list-inside space-y-1 pl-1">
                            {(item.actions as string[]).map((act, aIdx) => (
                              <li key={aIdx} className="text-foreground/90">{act}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1 border-t border-border/40 text-muted-foreground">
                          <div>
                            <span className="font-medium text-foreground">Assigned Route: </span>
                            <span className="text-emerald-400 font-semibold">{item.route as string}</span>
                          </div>
                          <div>
                            <span className="font-medium text-foreground">Target Shelter: </span>
                            <span>{item.target_shelter as string}</span>
                          </div>
                        </div>

                        {/* Explainable AI Drawer Trigger */}
                        <div className="p-2.5 bg-primary/5 rounded border border-primary/20 text-xs space-y-1">
                          <div className="flex items-center justify-between text-primary font-bold text-[11px]">
                            <span className="flex items-center gap-1">
                              <Info className="w-3.5 h-3.5" />
                              WHY THIS DECISION?
                            </span>
                            <span>Confidence: {((item.confidence as number) * 100).toFixed(0)}%</span>
                          </div>
                          <p className="text-[11px] text-muted-foreground">{item.reasoning as string}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-center py-16 text-muted-foreground text-sm space-y-2">
                  <HelpCircle className="w-8 h-8 mx-auto text-muted-foreground/60" />
                  <p>No operational plan generated yet.</p>
                  <p className="text-xs">Run the Multi-Agent Workflow from the Agent Operations tab to synthesize a response proposal.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Col: Safety & Governance Audit */}
        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-bold text-foreground">
                Safety Critic Audit
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="p-3 bg-muted rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Verification Check:</span>
                  <Badge className={criticPassed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}>
                    {criticPassed ? 'PASSED CLEAN' : 'FAIL / RE-PLAN'}
                  </Badge>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Validates zero resource over-allocations, route blockages, and shelter capacity limits before commander authorization.
                </p>
              </div>

              {criticResult?.reasons && (criticResult.reasons as string[]).length > 0 && (
                <div className="space-y-1.5">
                  <p className="font-semibold text-red-400">Detected Violations:</p>
                  <div className="p-2 bg-red-500/10 rounded border border-red-500/20 text-red-400 text-[11px] space-y-1">
                    {(criticResult.reasons as string[]).map((r, i) => (
                      <div key={i}>⚠️ {r}</div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-bold text-foreground">
                Governance Audit Log
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="p-2.5 bg-muted/40 rounded border border-border/60 space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-bold text-foreground">HUMAN_COMMANDER</span>
                  <span className="text-muted-foreground font-mono">{new Date().toLocaleTimeString()}</span>
                </div>
                <p className="text-muted-foreground text-[11px]">
                  Action: {approvalStatus} (Execution Mode: {executionStatus})
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
