"""Response Planner Agent synthesizing full operational plan."""
import logging
from datetime import datetime
from typing import Dict, Any, List
from app.graph.crisis_state import CrisisState
from app.llm.provider import get_llm_provider

logger = logging.getLogger(__name__)


class ResponsePlannerAgent:
    """Agent responsible for combining all specialized intelligence outputs 
    into a structured operational disaster response proposal."""

    def __init__(self):
        self.name = "RESPONSE_PLANNER"
        self.llm = get_llm_provider()

    async def run(self, state: CrisisState) -> CrisisState:
        """Synthesize verified agent outputs into actionable plan."""
        state.record_step(
            agent=self.name,
            action="SYNTHESIZE_RESPONSE_PLAN",
            status="STARTED",
            summary="Synthesizing intelligence into structured action items."
        )

        action_items = []
        priority_index = 1

        for zone in state.priority_zones:
            zid = zone.get("zone_id")
            zname = zone.get("zone_name")
            category = zone.get("category", "GREEN")

            alloc = state.resource_plan.get("allocations", {}).get(zid, {}).get("assigned_resources", {}) if state.resource_plan else {}
            routes = state.evacuation_plan.get(zid, {}) if state.evacuation_plan else {}

            if category in ["RED", "BLACK"]:
                actions_list = [
                    f"Initiate priority evacuation of {zname} (Population: {zone.get('population', 0):,})",
                    f"Deploy rescue assets: {alloc.get('rescue_teams', 2)} rescue teams, {alloc.get('rescue_boats', 2)} boats",
                    f"Pre-position {alloc.get('ambulances', 3)} ambulances at Route C staging point"
                ]

                primary_rt = routes.get("primary_route", {}).get("name", "Route C")

                action_items.append({
                    "priority": priority_index,
                    "zone": zname,
                    "risk_category": category,
                    "actions": actions_list,
                    "allocated_resources": alloc,
                    "route": primary_rt,
                    "target_shelter": routes.get("target_shelter", "Central Relief Shelter"),
                    "reasoning": f"High flood/structural risk ({zone.get('damage_severity')}% damage severity) combined with high population exposure.",
                    "evidence": [e.get("detail") for e in state.evidence[:3]],
                    "assumptions": state.assumptions[-2:],
                    "confidence": round((state.confidence_scores.get("RISK_AGENT", 0.9) + state.confidence_scores.get("RESOURCE_AGENT", 0.9)) / 2, 2),
                    "dependencies": ["Route C clearance", "Shelter capacity availability"],
                    "next_reassessment_mins": 15
                })
                priority_index += 1

        # Use LLM to refine executive summary if available
        llm_prompt = f"Draft an executive operational summary for Incident Commander based on {len(action_items)} priority action items for {state.incident_type}."
        exec_summary = await self.llm.generate_text(llm_prompt)
        if not exec_summary:
            exec_summary = (
                f"CRISISMIND OPERATIONAL RESPONSE PLAN FOR {state.incident_type.upper()} EMERGENCY: "
                f"Generated {len(action_items)} prioritized zone action plans. Primary focus on {action_items[0]['zone'] if action_items else 'affected zones'}. "
                f"Continuous reassessment cycle set to 15 minutes."
            )

        state.response_plan = {
            "incident_id": state.incident_id,
            "incident_type": state.incident_type,
            "executive_summary": exec_summary,
            "priority_action_items": action_items,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "PROPOSED",
            "replan_count": state.replan_count
        }

        state.record_step(
            agent=self.name,
            action="SYNTHESIZE_RESPONSE_PLAN",
            status="COMPLETED",
            summary=f"Operational plan synthesized with {len(action_items)} priority action blocks.",
            confidence=0.95
        )

        return state
