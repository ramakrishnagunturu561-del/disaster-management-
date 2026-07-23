"""Real LangGraph StateGraph Workflow Orchestrator for CrisisMind AI Phase 3 with Targeted Re-planning."""
import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
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


# Instantiate Agent Instances
supervisor_agent = SupervisorAgent()
vision_agent = VisionAgent()
nlp_agent = EmergencyIntelligenceAgent()
weather_agent = WeatherAgent()
sensor_agent = SensorAgent()
risk_agent = RiskAssessmentAgent()
resource_agent = ResourceAllocationAgent()
route_agent = EvacuationRouteAgent()
planner_agent = ResponsePlannerAgent()
critic_agent = CriticSafetyAgent()


# Node functions for LangGraph StateGraph
async def node_supervisor(state: CrisisState) -> CrisisState:
    return await supervisor_agent.run(state)

async def node_vision(state: CrisisState) -> CrisisState:
    return await vision_agent.run(state)

async def node_intelligence(state: CrisisState) -> CrisisState:
    return await nlp_agent.run(state)

async def node_weather(state: CrisisState) -> CrisisState:
    return await weather_agent.run(state)

async def node_sensor(state: CrisisState) -> CrisisState:
    return await sensor_agent.run(state)

async def node_risk(state: CrisisState) -> CrisisState:
    return await risk_agent.run(state)

async def node_resource(state: CrisisState) -> CrisisState:
    return await resource_agent.run(state)

async def node_route(state: CrisisState) -> CrisisState:
    return await route_agent.run(state)

async def node_planner(state: CrisisState) -> CrisisState:
    return await planner_agent.run(state)

async def node_critic(state: CrisisState) -> CrisisState:
    return await critic_agent.run(state)


def route_critic_evaluation(state: CrisisState) -> str:
    """LangGraph conditional edge router based on Critic safety evaluation."""
    if state.critic_result and state.critic_result.passed:
        return "end_workflow"
    
    # Check max replan protection limit
    if state.replan_count >= state.max_replan_limit:
        state.workflow_status = "HUMAN_REVIEW_REQUIRED"
        state.approval_status = "HUMAN_REVIEW_REQUIRED"
        state.warnings.append(
            f"Maximum re-plan attempts reached ({state.replan_count}/{state.max_replan_limit}). Automated self-correction stopped. Human Commander review required."
        )
        return "end_workflow"

    # Increment replan count & store previous decision version in history
    state.replan_count += 1
    if state.response_plan:
        state.decision_history.append({
            "version": state.decision_version,
            "response_plan": state.response_plan,
            "critic_result": state.critic_result.model_dump() if state.critic_result else None,
            "replan_targets": state.replan_targets
        })
        state.decision_version += 1

    # Targeted replan routing based on violation codes & replan targets
    targets = state.replan_targets or []
    if "resource_agent" in targets:
        return "replan_resource"
    elif "route_agent" in targets:
        return "replan_route"
    else:
        return "replan_planner"


def build_langgraph_workflow():
    """Construct real LangGraph StateGraph flow for Phase 3 with Safety Critic & Targeted Re-planning."""
    builder = StateGraph(CrisisState)

    # Add Nodes
    builder.add_node("supervisor", node_supervisor)
    builder.add_node("vision", node_vision)
    builder.add_node("intelligence", node_intelligence)
    builder.add_node("weather", node_weather)
    builder.add_node("sensor", node_sensor)
    builder.add_node("risk", node_risk)
    builder.add_node("resource", node_resource)
    builder.add_node("route", node_route)
    builder.add_node("planner", node_planner)
    builder.add_node("critic", node_critic)

    # Define Graph Edges:
    # START -> SUPERVISOR -> [VISION, INTELLIGENCE, WEATHER, SENSOR] -> RISK -> [RESOURCE, ROUTE] -> PLANNER -> CRITIC
    builder.add_edge(START, "supervisor")
    
    # Intelligence Collection Edges
    builder.add_edge("supervisor", "vision")
    builder.add_edge("vision", "intelligence")
    builder.add_edge("intelligence", "weather")
    builder.add_edge("weather", "sensor")
    
    # Risk Aggregation Edge
    builder.add_edge("sensor", "risk")
    
    # Operational Planning Edges
    builder.add_edge("risk", "resource")
    builder.add_edge("resource", "route")
    builder.add_edge("route", "planner")
    builder.add_edge("planner", "critic")

    # Conditional Routing Edge from Critic Node
    builder.add_conditional_edges(
        "critic",
        route_critic_evaluation,
        {
            "end_workflow": END,
            "replan_resource": "resource",
            "replan_route": "route",
            "replan_planner": "planner"
        }
    )

    return builder.compile()


class CrisisMindWorkflow:
    """Class wrapper executing the compiled LangGraph StateGraph."""

    def __init__(self):
        self.graph = build_langgraph_workflow()

    async def execute(self, state: CrisisState) -> CrisisState:
        """Execute compiled LangGraph flow."""
        state.workflow_status = "RUNNING"
        final_state_dict = await self.graph.ainvoke(state)
        
        # If StateGraph returns dict or Pydantic instance
        if isinstance(final_state_dict, CrisisState):
            final_state = final_state_dict
        else:
            final_state = CrisisState(**final_state_dict)

        if final_state.critic_result and not final_state.critic_result.passed and final_state.replan_count >= final_state.max_replan_limit:
            final_state.workflow_status = "HUMAN_REVIEW_REQUIRED"
            final_state.approval_status = "HUMAN_REVIEW_REQUIRED"
        elif final_state.critic_result and final_state.critic_result.passed:
            final_state.workflow_status = "AWAITING_HUMAN_APPROVAL"

        return final_state


# Singleton instance
_workflow_instance: Optional[CrisisMindWorkflow] = None

def get_crisis_workflow() -> CrisisMindWorkflow:
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = CrisisMindWorkflow()
    return _workflow_instance
