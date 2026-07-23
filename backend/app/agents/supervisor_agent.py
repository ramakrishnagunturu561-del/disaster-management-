"""Incident Commander / Supervisor Agent."""
import logging
from typing import List
from app.graph.crisis_state import CrisisState
from app.llm.provider import get_llm_provider

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Incident Commander Agent responsible for classifying emergency, 
    determining workflow pipeline, and orchestrating downstream agents."""

    def __init__(self):
        self.name = "INCIDENT_COMMANDER"
        self.llm = get_llm_provider()

    async def run(self, state: CrisisState) -> CrisisState:
        """Evaluate incident and route to required specialized intelligence agents."""
        state.record_step(
            agent=self.name,
            action="CLASSIFY_INCIDENT_AND_ROUTE",
            status="STARTED",
            summary=f"Analyzing incident {state.incident_id} ({state.incident_type})"
        )

        incident_type = state.incident_type.lower()
        has_image = bool(state.drone_image_bytes)
        has_text = bool(state.emergency_text_reports)

        # Phase 1 Conditional Routing Logic
        required_agents = []

        if has_image:
            required_agents.append("VISION_AGENT")
        if has_text or not has_image:
            required_agents.append("EMERGENCY_INTELLIGENCE_AGENT")

        required_agents.extend(["RISK_AGENT", "RESPONSE_PLANNER"])

        # Store routing plan in state assumptions & metadata
        state.assumptions.append(
            f"Supervisor classification: '{incident_type.upper()}'. Pipeline routing: {', '.join(required_agents)}."
        )

        # Optional LLM enhancement for classification summary
        llm_prompt = f"Summarize the incident commander's initial tactical assessment for a {incident_type} disaster at coordinates {state.location}."
        summary = await self.llm.generate_text(llm_prompt)
        if not summary:
            summary = (
                f"Incident Commander initiated tactical workflow for {incident_type.upper()} scenario. "
                f"Routing to specialized agents: {', '.join(required_agents)}."
            )

        state.assumptions.append(f"Disaster type classified as '{incident_type.upper()}'. Parallel intelligence pipeline activated.")

        state.record_step(
            agent=self.name,
            action="CLASSIFY_INCIDENT_AND_ROUTE",
            status="COMPLETED",
            summary=summary,
            confidence=0.95
        )

        return state
