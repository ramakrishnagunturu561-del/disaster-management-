"""Real LangGraph StateGraph Workflow Orchestrator for CrisisMind AI Phase 2."""
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


def build_langgraph_workflow():
    """Construct real LangGraph StateGraph flow for Phase 2."""
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

    # Define Graph Edges:
    # START -> SUPERVISOR -> [VISION, INTELLIGENCE, WEATHER, SENSOR] -> RISK -> [RESOURCE, ROUTE] -> PLANNER -> END
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
    
    # Completion Edge
    builder.add_edge("planner", END)

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

        final_state.workflow_status = "COMPLETED"
        return final_state


# Singleton instance
_workflow_instance: Optional[CrisisMindWorkflow] = None

def get_crisis_workflow() -> CrisisMindWorkflow:
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = CrisisMindWorkflow()
    return _workflow_instance
