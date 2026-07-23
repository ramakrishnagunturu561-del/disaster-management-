"""LangGraph / State Machine Workflow Orchestrator for CrisisMind AI."""
import logging
from typing import Dict, Any, Optional
from app.graph.crisis_state import CrisisState
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.vision_agent import VisionAgent
from app.agents.intelligence_agent import EmergencyIntelligenceAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.sensor_agent import SensorAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.resource_agent import ResourceAllocationAgent
from app.agents.route_agent import EvacuationRouteAgent
from app.agents.response_planner_agent import ResponsePlannerAgent
from app.agents.critic_agent import CriticSafetyAgent

logger = logging.getLogger(__name__)


class CrisisMindWorkflow:
    """Orchestrates the multi-agent graph state machine."""

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.vision = VisionAgent()
        self.nlp = EmergencyIntelligenceAgent()
        self.weather = WeatherAgent()
        self.sensor = SensorAgent()
        self.risk = RiskAssessmentAgent()
        self.resource = ResourceAllocationAgent()
        self.route = EvacuationRouteAgent()
        self.planner = ResponsePlannerAgent()
        self.critic = CriticSafetyAgent()

    async def execute(self, state: CrisisState) -> CrisisState:
        """Run full multi-agent crisis state machine."""
        state.workflow_status = "RUNNING"
        
        # 1. Incident Commander / Supervisor
        state = await self.supervisor.run(state)

        # 2. Parallel Intelligence Agents
        state = await self.vision.run(state)
        state = await self.nlp.run(state)
        state = await self.weather.run(state)
        state = await self.sensor.run(state)

        # 3. Risk Assessment Agent
        state = await self.risk.run(state)

        # 4. Planning & Optimization Agents
        state = await self.resource.run(state)
        state = await self.route.run(state)

        # 5. Response Planner Agent
        state = await self.planner.run(state)

        # 6. Safety Critic Agent
        state = await self.critic.run(state)

        # 7. Self-Correction Loop check
        while state.critic_result and not state.critic_result.passed and state.replan_count < state.max_replan_limit:
            logger.info(f"Re-planning loop triggered. Replan count: {state.replan_count}/{state.max_replan_limit}")
            # Re-adjust resource constraints or shelter allocations
            state.available_resources["rescue_teams"] += 2  # Adjust inventory during replan
            state = await self.resource.run(state)
            state = await self.route.run(state)
            state = await self.planner.run(state)
            state = await self.critic.run(state)

        if state.critic_result and state.critic_result.passed:
            state.workflow_status = "NEEDS_HUMAN_APPROVAL"
        else:
            state.workflow_status = "COMPLETED"

        return state


# Singleton instance
_workflow_instance: Optional[CrisisMindWorkflow] = None

def get_crisis_workflow() -> CrisisMindWorkflow:
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = CrisisMindWorkflow()
    return _workflow_instance
