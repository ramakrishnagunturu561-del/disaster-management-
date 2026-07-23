"""Critic / Safety Verification Agent."""
import logging
from typing import List
from app.graph.crisis_state import CrisisState, CriticResult

logger = logging.getLogger(__name__)


class CriticSafetyAgent:
    """Mandatory Critic Agent responsible for safety verification, constraint checking, 
    and triggering re-planning loops if invalid."""

    def __init__(self):
        self.name = "CRITIC_AGENT"

    async def run(self, state: CrisisState) -> CrisisState:
        """Run safety and operational sanity checks on the proposed response plan."""
        state.record_step(
            agent=self.name,
            action="VERIFY_SAFETY_AND_CONSTRAINTS",
            status="STARTED",
            summary="Auditing proposed plan against safety constraints and resource capacities."
        )

        failures: List[str] = []

        # 1. Resource Availability Check
        if state.resource_plan:
            totals = state.resource_plan.get("total_allocated", {})
            avail = state.resource_plan.get("initial_inventory", {})
            for rtype, count in totals.items():
                if count > avail.get(rtype, 0):
                    failures.append(f"Resource over-allocation: Planned {count} {rtype}, but only {avail.get(rtype, 0)} available.")

        # 2. Shelter Capacity Check
        if state.evacuation_plan:
            for zid, plan in state.evacuation_plan.items():
                remaining_cap = plan.get("shelter_capacity_remaining", 0)
                if remaining_cap <= 0:
                    failures.append(f"Shelter capacity exceeded for zone {plan.get('zone_name')}.")

        # 3. Route Validity Check
        if state.route_analysis:
            blocked = state.route_analysis.get("blocked_corridors", [])
            if state.response_plan:
                for item in state.response_plan.get("priority_action_items", []):
                    used_route = item.get("route")
                    if used_route in blocked:
                        failures.append(f"Invalid route: Plan uses blocked corridor '{used_route}' for {item.get('zone')}.")

        # 4. Confidence Threshold Check
        if state.confidence_scores:
            avg_conf = sum(state.confidence_scores.values()) / len(state.confidence_scores)
            if avg_conf < 0.5:
                failures.append(f"Confidence score below safety threshold ({avg_conf:.2f} < 0.50).")

        # 5. Simulated Re-plan Check for Demo (triggers 1 loop if forced for validation testing)
        if state.replan_count == 0 and state.warnings and "DEMO_REPLAN_TEST" in state.warnings:
            failures.append("Simulated safety critic alert: Initial shelter capacity constraint conflict detected in Zone A.")

        if failures:
            passed = False
            state.critic_result = CriticResult(passed=False, reasons=failures, confidence=0.98)
            state.workflow_status = "REPLANNING"
            state.replan_count += 1
            summary_msg = f"CRITIC FAIL ({len(failures)} safety violations). Triggering re-planning loop (Count: {state.replan_count}/{state.max_replan_limit})."
        else:
            passed = True
            state.critic_result = CriticResult(passed=True, reasons=[], confidence=0.99)
            state.workflow_status = "NEEDS_HUMAN_APPROVAL"
            summary_msg = "CRITIC PASS. Operational plan verified clean. Ready for Incident Commander approval."

        state.record_step(
            agent=self.name,
            action="VERIFY_SAFETY_AND_CONSTRAINTS",
            status="COMPLETED" if passed else "FAILED",
            summary=summary_msg,
            confidence=0.99,
            errors=failures if not passed else None
        )

        return state
