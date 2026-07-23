"""Unit and Integration tests for CrisisMind AI Multi-Agent Architecture."""
import pytest
import pytest_asyncio
from app.graph.crisis_state import CrisisState
from app.graph.crisis_graph import CrisisMindWorkflow
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.resource_agent import ResourceAllocationAgent
from app.agents.critic_agent import CriticSafetyAgent


@pytest.mark.asyncio
async def test_supervisor_agent_routing():
    """Verify Supervisor Agent classifies disaster and populates assumptions."""
    supervisor = SupervisorAgent()
    state = CrisisState(
        incident_id="test-01",
        incident_type="flood",
        title="Urban Flood Emergency"
    )
    res_state = await supervisor.run(state)
    assert res_state.current_agent == "INCIDENT_COMMANDER"
    assert len(res_state.agent_history) >= 1
    assert "FLOOD" in res_state.assumptions[0]


@pytest.mark.asyncio
async def test_risk_assessment_agent():
    """Verify Risk Agent calculates zone priority and modeled survival-risk indicators."""
    risk_agent = RiskAssessmentAgent()
    state = CrisisState(
        incident_id="test-02",
        incident_type="flood",
        priority_zones=[
            {"id": "00000000-0000-0000-0000-000000000001", "name": "Riverfront Zone A", "population": 12000, "damage_score": 80.0}
        ]
    )
    res_state = await risk_agent.run(state)
    assert res_state.risk_assessment is not None
    assert len(res_state.priority_zones) > 0
    top_zone = res_state.priority_zones[0]
    assert "modeled_survival_risk_indicator" in top_zone
    assert "priority_score" in top_zone


@pytest.mark.asyncio
async def test_resource_agent_constraints():
    """Verify Resource Allocation Agent respects availability constraints."""
    resource_agent = ResourceAllocationAgent()
    state = CrisisState(
        incident_id="test-03",
        incident_type="flood",
        available_resources={"rescue_teams": 3, "ambulances": 5},
        priority_zones=[
            {"zone_id": "z1", "zone_name": "Critical Zone 1", "category": "RED"}
        ]
    )
    res_state = await resource_agent.run(state)
    assert res_state.resource_plan is not None
    totals = res_state.resource_plan["total_allocated"]
    assert totals["rescue_teams"] <= 3
    assert totals["ambulances"] <= 5


@pytest.mark.asyncio
async def test_critic_agent_pass_and_fail():
    """Verify Safety Critic passes valid plans and flags invalid ones."""
    critic = CriticSafetyAgent()
    
    # Valid state
    state_valid = CrisisState(
        incident_id="test-04",
        incident_type="flood",
        available_resources={"rescue_teams": 10},
        resource_plan={"initial_inventory": {"rescue_teams": 10}, "total_allocated": {"rescue_teams": 5}}
    )
    res_valid = await critic.run(state_valid)
    assert res_valid.critic_result.passed is True

    # Invalid state (over-allocation)
    state_invalid = CrisisState(
        incident_id="test-05",
        incident_type="flood",
        available_resources={"rescue_teams": 5},
        resource_plan={"initial_inventory": {"rescue_teams": 5}, "total_allocated": {"rescue_teams": 12}}
    )
    res_invalid = await critic.run(state_invalid)
    assert res_invalid.critic_result.passed is False
    assert len(res_invalid.critic_result.reasons) > 0


@pytest.mark.asyncio
async def test_full_agent_workflow_execution():
    """Test end-to-end execution of the multi-agent graph state machine."""
    workflow = CrisisMindWorkflow()
    state = CrisisState(
        incident_id="demo-vijayawada",
        incident_type="flood",
        title="Vijayawada Urban Flood Emergency"
    )
    final_state = await workflow.execute(state)
    assert final_state.workflow_status in ["COMPLETED", "NEEDS_HUMAN_APPROVAL"]
    assert len(final_state.agent_history) >= 10
    assert final_state.response_plan is not None
    assert final_state.critic_result is not None
