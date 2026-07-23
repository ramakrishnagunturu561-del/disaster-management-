"""Critic / Safety Verification Agent orchestrating deterministic validators."""
import logging
from datetime import datetime
from typing import Dict, Any, List
from app.graph.crisis_state import CrisisState, CriticResult
from app.validators.resource_validator import validate_resources
from app.validators.shelter_validator import validate_shelters
from app.validators.route_validator import validate_routes
from app.validators.weather_validator import validate_weather
from app.validators.evidence_validator import validate_evidence
from app.validators.plan_validator import validate_plan_consistency

logger = logging.getLogger(__name__)


class CriticSafetyAgent:
    """Independent Safety Critic Agent running deterministic validators against plan outputs."""

    def __init__(self):
        self.name = "CRITIC_AGENT"
        self.version = "1.0.0"

    async def run(self, state: CrisisState) -> CrisisState:
        """Run all deterministic validators against current state."""
        state.record_step(
            agent=self.name,
            action="VERIFY_SAFETY_AND_CONSTRAINTS",
            status="STARTED",
            summary="Auditing operational response plan against deterministic safety constraints."
        )

        all_violations: List[Dict[str, Any]] = []

        # 1. Resource Validator
        res_inv = state.available_resources
        all_violations.extend(validate_resources(state.resource_plan or {}, res_inv))

        # 2. Shelter Validator
        all_violations.extend(validate_shelters(state.evacuation_plan or {}, state.priority_zones or []))

        # 3. Route Validator
        all_violations.extend(validate_routes(state.route_analysis or {}, state.evacuation_plan or {}, state.response_plan or {}))

        # 4. Weather Validator
        all_violations.extend(validate_weather(state.weather_intelligence or {}))

        # 5. Evidence Validator
        all_violations.extend(validate_evidence(state.evidence or [], state.response_plan or {}))

        # 6. Plan Consistency Validator
        all_violations.extend(validate_plan_consistency(state.response_plan or {}, state.priority_zones or []))

        # Categorize violations by severity
        critical_high_violations = [v for v in all_violations if v.get("severity") in ["CRITICAL", "HIGH"]]
        warning_violations = [v for v in all_violations if v.get("severity") == "WARNING"]

        # Determine target agents for re-planning based on violation codes
        replan_targets = list(set([v.get("responsible_agent") for v in critical_high_violations if v.get("responsible_agent")]))

        if critical_high_violations:
            status = "FAIL"
            passed = False
            score = max(0, 100 - len(critical_high_violations) * 25)
        elif warning_violations:
            status = "PASS_WITH_WARNINGS"
            passed = True
            score = max(60, 100 - len(warning_violations) * 10)
        else:
            status = "PASS"
            passed = True
            score = 100

        # Construct structured Critic Result
        critic_dict = {
            "status": status,
            "overall_score": score,
            "violations": critical_high_violations,
            "warnings": [w.get("message") for w in warning_violations],
            "validated_constraints": ["RESOURCE_LIMITS", "SHELTER_CAPACITY", "ROUTE_SAFETY", "DATA_AGE", "EVIDENCE_TRACEABILITY"],
            "required_replan_targets": replan_targets,
            "timestamp": datetime.utcnow().isoformat(),
            "validator_version": self.version
        }

        reason_strings = [v.get("message", "") for v in critical_high_violations]

        state.critic_result = CriticResult(
            passed=passed,
            reasons=reason_strings,
            confidence=0.99,
            timestamp=critic_dict["timestamp"]
        )

        state.unresolved_violations = all_violations
        state.replan_targets = replan_targets

        if passed:
            state.workflow_status = "AWAITING_HUMAN_APPROVAL"
            state.approval_status = "PROPOSED"
            summary_msg = f"CRITIC {status} (Score: {score}/100). Plan verified clean. Awaiting Commander authorization."
        else:
            state.replan_count += 1
            if state.replan_count >= state.max_replan_limit:
                state.workflow_status = "HUMAN_REVIEW_REQUIRED"
                state.approval_status = "HUMAN_REVIEW_REQUIRED"
                summary_msg = f"CRITIC FAIL (Score: {score}/100). Maximum re-plan attempts reached ({state.replan_count}/{state.max_replan_limit}). Automated self-correction stopped. Human Commander review required."
            else:
                summary_msg = f"CRITIC FAIL (Score: {score}/100, {len(critical_high_violations)} Critical/High Violations). Targeted Re-plan required: {', '.join(replan_targets)}."

        state.record_step(
            agent=self.name,
            action="VERIFY_SAFETY_AND_CONSTRAINTS",
            status="COMPLETED" if passed else "FAILED",
            summary=summary_msg,
            confidence=0.99,
            errors=reason_strings if not passed else None
        )

        return state
