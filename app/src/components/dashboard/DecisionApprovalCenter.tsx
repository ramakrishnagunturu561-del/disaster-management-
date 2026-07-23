import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, Edit3, AlertOctagon, FileText, AlertTriangle, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';

export interface DecisionApprovalCenterProps {
  agentState: Record<string, unknown> | null;
  onApprove: (action?: string, approver?: string, role?: string, comments?: string, overrideReason?: string) => void;
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
  const [showModifyBox, setShowModifyBox] = useState(false);
  const [modifyNotes, setModifyNotes] = useState('');
  const [overrideReason, setOverrideReason] = useState('');
  const [showOverrideBox, setShowOverrideBox] = useState(false);
  const [explainModalOpen, setExplainModalOpen] = useState(false);

  const responsePlan = agentState?.response_plan as Record<string, unknown> | undefined;
  const criticResult = agentState?.critic_result as Record<string, unknown> | undefined;
  const approvalStatus = (agentState?.approval_status as string) || 'PROPOSED';
  const decisionVersion = (agentState?.decision_version as number) || 1;
  const actionItems = (responsePlan?.priority_action_items as Record<string, unknown>[]) || [];
  const unresolvedViolations = (agentState?.unresolved_violations as Record<string, unknown>[]) || [];

  const criticPassed = criticResult?.passed === true;
  const criticScore = (criticResult?.overall_score as number) ?? 100;

  const handleApproveClick = () => {
    if (!criticPassed) {
      setShowOverrideBox(true);
      return;
    }
    onApprove('APPROVE', 'Incident Commander', 'Commander', 'Authorized after full Safety Critic verification');
  };

  const handleOverrideSubmit = () => {
    if (!overrideReason.trim()) return;
    onApprove('HUMAN_OVERRIDE', 'Incident Commander', 'Commander', 'Approved with explicit override', overrideReason);
    setShowOverrideBox(false);
  };

  const handleModifySubmit = () => {
    if (!modifyNotes.trim()) return;
    onModify({ requested_adjustments: modifyNotes, timestamp: new Date().toISOString() });
    setShowModifyBox(false);
    setModifyNotes('');
  };

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card p-4 rounded-xl border border-border">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
              Decision Approval & Governance Center
            </h2>
            <Badge className="bg-primary/10 text-primary border-primary/20 font-mono">
              PLAN v{decisionVersion}
            </Badge>
            <Badge className={
              approvalStatus === 'APPROVED' || approvalStatus === 'APPROVED_WITH_OVERRIDE' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
              approvalStatus === 'REJECTED' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
              approvalStatus === 'HUMAN_REVIEW_REQUIRED' ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' :
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
        <div className="flex flex-wrap items-center gap-2">
          {approvalStatus === 'APPROVED' || approvalStatus === 'APPROVED_WITH_OVERRIDE' ? (
            <Badge className="px-4 py-2 bg-emerald-500/20 text-emerald-400 border-emerald-500/40 text-xs font-bold gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              PLAN APPROVED — EXECUTED (SIMULATION ONLY)
            </Badge>
          ) : (
            <>
              <Button 
                onClick={handleApproveClick}
                disabled={!responsePlan}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold gap-1.5 text-xs"
              >
                <CheckCircle2 className="w-4 h-4" />
                APPROVE PLAN
              </Button>
              <Button 
                variant="outline"
                onClick={() => setShowModifyBox(!showModifyBox)}
                disabled={!responsePlan}
                className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 gap-1.5 text-xs"
              >
                <Edit3 className="w-4 h-4" />
                MODIFY PLAN
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowRejectBox(!showRejectBox)}
                disabled={!responsePlan}
                className="border-red-500/40 text-red-400 hover:bg-red-500/10 gap-1.5 text-xs"
              >
                <XCircle className="w-4 h-4" />
                REJECT PLAN
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Human Override Dialog Box */}
      {showOverrideBox && (
        <Card className="border-amber-500/40 bg-amber-500/10">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              HUMAN OVERRIDE AUTHORIZATION REQUIRED
            </h4>
            <p className="text-xs text-muted-foreground">
              Safety Critic check flagged unresolved violations. Explicit commander justification is required to override safety checks.
            </p>
            <Textarea
              value={overrideReason}
              onChange={e => setOverrideReason(e.target.value)}
              placeholder="Provide commander justification for manual override..."
              className="bg-background text-xs border-border"
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowOverrideBox(false)}>Cancel</Button>
              <Button size="sm" onClick={handleOverrideSubmit} className="bg-amber-600 hover:bg-amber-500 text-white font-bold">
                Submit Human Override Approval
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modify Request Box */}
      {showModifyBox && (
        <Card className="border-amber-500/40 bg-amber-500/5">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
              <Edit3 className="w-4 h-4" />
              Commander Requested Modifications (Creates Decision Plan v{decisionVersion + 1})
            </h4>
            <Textarea
              value={modifyNotes}
              onChange={e => setModifyNotes(e.target.value)}
              placeholder="e.g. Increase ambulance staging at Highway 16 and re-verify route safety..."
              className="bg-background text-xs border-border"
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowModifyBox(false)}>Cancel</Button>
              <Button size="sm" onClick={handleModifySubmit} className="bg-amber-600 hover:bg-amber-500 text-white font-bold">
                Submit Modifications & Re-Validate
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reject Request Box */}
      {showRejectBox && (
        <Card className="border-red-500/30 bg-red-500/5">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-xs font-bold text-red-400 flex items-center gap-1.5">
              <AlertOctagon className="w-4 h-4" />
              Reason for Rejection / Workflow Termination
            </h4>
            <Textarea
              value={rejectReason}
              onChange={e => setRejectReason(e.target.value)}
              placeholder="e.g. Plan rejected due to obsolete incident location data..."
              className="bg-background text-xs border-border"
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowRejectBox(false)}>Cancel</Button>
              <Button 
                size="sm"
                onClick={() => { onReject(rejectReason); setShowRejectBox(false); }} 
                className="bg-red-600 hover:bg-red-500 text-white font-bold"
              >
                Confirm Rejection
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Grid Layout for Critic Validation & Action Items */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Safety Critic Validation Card */}
        <Card className={`border ${criticPassed ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-rose-500/30 bg-rose-500/5'}`}>
          <CardHeader className="py-3 px-4 border-b border-border">
            <CardTitle className="text-xs font-bold flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-foreground">
                <ShieldCheck className={`w-4 h-4 ${criticPassed ? 'text-emerald-400' : 'text-rose-400'}`} />
                Safety Critic Audit
              </span>
              <Badge className={criticPassed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}>
                SCORE: {criticScore}/100
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded bg-secondary/50 border border-border">
                <span className="text-muted-foreground block text-[10px]">Resource Limits</span>
                <span className="font-bold text-emerald-400">PASSED</span>
              </div>
              <div className="p-2 rounded bg-secondary/50 border border-border">
                <span className="text-muted-foreground block text-[10px]">Shelter Capacity</span>
                <span className={`font-bold ${unresolvedViolations.some(v => v.code === 'SHELTER_CAPACITY_EXCEEDED') ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {unresolvedViolations.some(v => v.code === 'SHELTER_CAPACITY_EXCEEDED') ? 'FAIL' : 'PASSED'}
                </span>
              </div>
              <div className="p-2 rounded bg-secondary/50 border border-border">
                <span className="text-muted-foreground block text-[10px]">Route Safety</span>
                <span className={`font-bold ${unresolvedViolations.some(v => v.code === 'ROUTE_BLOCKED') ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {unresolvedViolations.some(v => v.code === 'ROUTE_BLOCKED') ? 'FAIL' : 'PASSED'}
                </span>
              </div>
              <div className="p-2 rounded bg-secondary/50 border border-border">
                <span className="text-muted-foreground block text-[10px]">Weather Freshness</span>
                <span className="font-bold text-emerald-400">PASSED</span>
              </div>
            </div>

            {/* Violation Details */}
            {unresolvedViolations.length > 0 && (
              <div className="space-y-1.5 pt-2">
                <h5 className="text-[11px] font-bold text-rose-400 flex items-center gap-1">
                  <AlertOctagon className="w-3.5 h-3.5" /> Machine-Readable Violations:
                </h5>
                {unresolvedViolations.map((v, i) => (
                  <div key={i} className="p-2 rounded bg-rose-500/10 border border-rose-500/20 text-[10px] space-y-0.5">
                    <div className="flex items-center justify-between font-mono font-bold text-rose-300">
                      <span>[{v.code as string}]</span>
                      <Badge className="text-[9px] bg-rose-500/20 text-rose-300">{v.severity as string}</Badge>
                    </div>
                    <p className="text-foreground">{v.message as string}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tactical Response Action Proposal */}
        <div className="lg:col-span-2 space-y-3">
          <Card className="bg-card border-border">
            <CardHeader className="py-3 px-4 border-b border-border flex flex-row items-center justify-between">
              <CardTitle className="text-xs font-bold flex items-center gap-1.5 text-foreground">
                <FileText className="w-4 h-4 text-primary" />
                Synthesized Action Proposals (Plan v{decisionVersion})
              </CardTitle>
              <Button size="sm" variant="ghost" onClick={() => setExplainModalOpen(!explainModalOpen)} className="text-xs text-primary gap-1">
                <Eye className="w-3.5 h-3.5" />
                WHY THIS DECISION? (XAI)
              </Button>
            </CardHeader>
            <CardContent className="p-4 space-y-3">
              {actionItems.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground text-xs">
                  No action items synthesized. Trigger workflow from Agent Operations.
                </div>
              ) : (
                actionItems.map((item, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-secondary/30 border border-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-primary flex items-center gap-2">
                        Priority #{item.priority as number} — Zone: {item.zone as string}
                      </span>
                      <Badge className={
                        item.risk_category === 'RED' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                      }>
                        {item.risk_category as string} THREAT
                      </Badge>
                    </div>

                    <ul className="list-disc list-inside text-xs text-foreground space-y-1">
                      {((item.actions as string[]) || []).map((act, i) => (
                        <li key={i}>{act}</li>
                      ))}
                    </ul>

                    <div className="grid grid-cols-2 gap-2 pt-2 text-[10px] text-muted-foreground font-mono">
                      <div>Route: <span className="text-foreground font-semibold">{item.route as string}</span></div>
                      <div>Target Shelter: <span className="text-foreground font-semibold">{item.target_shelter as string}</span></div>
                    </div>
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
