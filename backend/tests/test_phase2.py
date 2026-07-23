"""Unit and integration test suite for CrisisMind AI Phase 2 Operational Agents."""
import os
import sys
import asyncio
import pytest

os.environ["SKIP_TRANSFORMER_DOWNLOAD"] = "1"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.crisis_state import CrisisState
from app.graph.crisis_graph import get_crisis_workflow, build_langgraph_workflow
from app.agents.weather_agent import WeatherAgent
from app.agents.sensor_agent import SensorAgent
from app.agents.resource_agent import ResourceAllocationAgent
from app.agents.route_agent import EvacuationRouteAgent


@pytest.mark.asyncio
async def test_weather_agent_integration():
    """1. Test Weather Agent with Open-Meteo API or fallback handling."""
    agent = WeatherAgent()
    state = CrisisState(
        incident_id="phase2-w1",
        incident_type="flood",
        location={"latitude": 16.5062, "longitude": 80.6480}
    )
    res_state = await agent.run(state)
    assert res_state.weather_intelligence is not None
    assert "flood_risk_indicator" in res_state.weather_intelligence
    assert any(step.agent == "WEATHER_AGENT" for step in res_state.agent_history)


@pytest.mark.asyncio
async def test_sensor_agent_anomalies():
    """2. Test Sensor Agent processing IoT telemetry and detecting threshold violations."""
    agent = SensorAgent()
    state = CrisisState(
        incident_id="phase2-s1",
        incident_type="flood",
        sensor_readings=[
            {"sensor_id": "WL-01", "sensor_type": "water_level", "value": 5.2},
            {"sensor_id": "SEIS-01", "sensor_type": "seismic", "value": 2.1}
        ]
    )
    res_state = await agent.run(state)
    intel = res_state.sensor_intelligence
    assert intel is not None
    assert intel["anomaly_count"] >= 1
    assert len(intel["critical_violations"]) == 1
    assert intel["critical_violations"][0]["sensor_id"] == "WL-01"


@pytest.mark.asyncio
async def test_resource_agent_allocation_solver():
    """3. Test Resource Agent solving constrained allocation without over-allocating."""
    agent = ResourceAllocationAgent()
    state = CrisisState(
        incident_id="phase2-r1",
        incident_type="flood",
        available_resources={"rescue_teams": 4, "ambulances": 8, "rescue_boats": 3},
        priority_zones=[
            {"zone_id": "00000000-0000-0000-0000-00000000000a", "zone_name": "Downtown", "category": "RED"},
            {"zone_id": "00000000-0000-0000-0000-00000000000b", "zone_name": "Heights", "category": "YELLOW"}
        ]
    )
    res_state = await agent.run(state)
    plan = res_state.resource_plan
    assert plan is not None
    assert plan["status"] == "VALIDATED"
    totals = plan["total_allocated"]
    assert totals["rescue_teams"] <= 4
    assert totals["ambulances"] <= 8
    assert totals["rescue_boats"] <= 3


@pytest.mark.asyncio
async def test_route_agent_corridor_evaluation():
    """4. Test Route Agent evaluating evacuation routes and shelter capacities."""
    agent = EvacuationRouteAgent()
    state = CrisisState(
        incident_id="phase2-rt1",
        incident_type="flood",
        priority_zones=[
            {"zone_id": "00000000-0000-0000-0000-00000000000a", "zone_name": "Downtown", "category": "RED"}
        ],
        vision_analysis={"detections": [{"label": "Road Damage"}]}
    )
    res_state = await agent.run(state)
    plan = res_state.evacuation_plan
    assert plan is not None
    dt_plan = plan.get("00000000-0000-0000-0000-00000000000a")
    assert dt_plan is not None
    assert dt_plan["primary_route"]["status"] == "CLEAR"
    assert dt_plan["shelter_capacity_remaining"] > 0
    assert len(dt_plan["blocked_routes"]) > 0


@pytest.mark.asyncio
async def test_real_langgraph_stategraph_pipeline():
    """5. Test execution of the compiled real LangGraph StateGraph pipeline."""
    workflow = get_crisis_workflow()
    state = CrisisState(
        incident_id="vijayawada-phase2-demo",
        incident_type="flood",
        title="Vijayawada Urban Flood Emergency",
        emergency_text_reports=[{"text": "Trapped people near downtown riverbank", "source": "911"}],
        sensor_readings=[{"sensor_id": "WL-01", "sensor_type": "water_level", "value": 4.9}]
    )
    final_state = await workflow.execute(state)
    assert final_state.workflow_status in ["COMPLETED", "AWAITING_HUMAN_APPROVAL"]
    assert final_state.weather_intelligence is not None
    assert final_state.sensor_intelligence is not None
    assert final_state.resource_plan is not None
    assert final_state.evacuation_plan is not None
    assert final_state.response_plan is not None
    assert len(final_state.agent_history) >= 15


async def run_phase2_verification():
    """Run all Phase 2 tests synchronously."""
    print("==================================================")
    print(" CRISISMIND AI PHASE 2 OPERATIONAL AGENTS VERIFICATION")
    print("==================================================")

    print("[TEST 1/5] Weather Intelligence Agent (Open-Meteo REST)...")
    await test_weather_agent_integration()
    print("  --> PASS")

    print("[TEST 2/5] Sensor Intelligence Agent (IoT Telemetry)...")
    await test_sensor_agent_anomalies()
    print("  --> PASS")

    print("[TEST 3/5] Resource Allocation Agent (Constrained Solver)...")
    await test_resource_agent_allocation_solver()
    print("  --> PASS")

    print("[TEST 4/5] Evacuation Route Agent (Corridors & Shelters)...")
    await test_route_agent_corridor_evaluation()
    print("  --> PASS")

    print("[TEST 5/5] Real LangGraph StateGraph Execution Pipeline...")
    await test_real_langgraph_stategraph_pipeline()
    print("  --> PASS")

    print("==================================================")
    print(" ALL 5 PHASE 2 OPERATIONAL AGENT TESTS PASSED CLEANLY!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_phase2_verification())
