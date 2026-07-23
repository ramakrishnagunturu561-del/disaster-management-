"""Focused unit and integration test suite for CrisisMind AI Phase 1 Foundation."""
import os
import sys
import asyncio
import pytest

# Ensure fast execution without heavy downloads during tests
os.environ["SKIP_TRANSFORMER_DOWNLOAD"] = "1"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.crisis_state import CrisisState
from app.graph.crisis_graph import get_crisis_workflow
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.vision_agent import VisionAgent
from app.agents.intelligence_agent import EmergencyIntelligenceAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.response_planner_agent import ResponsePlannerAgent
from app.llm.provider import LLMProvider, get_llm_provider


@pytest.mark.asyncio
async def test_crisis_state_initialization():
    """1. Test CrisisState initialization and default values."""
    state = CrisisState(
        incident_id="inc-test-01",
        incident_type="flood",
        title="Vijayawada Flood Emergency",
        location={"latitude": 16.5062, "longitude": 80.6480}
    )
    assert state.incident_id == "inc-test-01"
    assert state.incident_type == "flood"
    assert state.location["latitude"] == 16.5062
    assert state.current_agent == "INCIDENT_COMMANDER"
    assert state.workflow_status == "INITIALIZED"
    assert isinstance(state.agent_history, list)


@pytest.mark.asyncio
async def test_supervisor_routing_flood():
    """2. Test Supervisor routing for flood (image + text)."""
    supervisor = SupervisorAgent()
    state = CrisisState(
        incident_id="inc-flood-01",
        incident_type="flood",
        drone_image_bytes=b"fake_image_bytes",
        emergency_text_reports=[{"text": "Flooding reported downtown", "source": "911"}]
    )
    res_state = await supervisor.run(state)
    assert res_state.current_agent == "INCIDENT_COMMANDER"
    assert "VISION_AGENT" in res_state.assumptions[0]
    assert "EMERGENCY_INTELLIGENCE_AGENT" in res_state.assumptions[0]


@pytest.mark.asyncio
async def test_supervisor_routing_text_only():
    """3. Test Supervisor routing for text-only emergency."""
    supervisor = SupervisorAgent()
    state = CrisisState(
        incident_id="inc-text-01",
        incident_type="flood",
        emergency_text_reports=[{"text": "Trapped residents near riverbank", "source": "call"}]
    )
    res_state = await supervisor.run(state)
    assert "EMERGENCY_INTELLIGENCE_AGENT" in res_state.assumptions[0]
    assert "VISION_AGENT" not in res_state.assumptions[0]


@pytest.mark.asyncio
async def test_supervisor_routing_structural_image():
    """4. Test Supervisor routing for image-based structural damage."""
    supervisor = SupervisorAgent()
    state = CrisisState(
        incident_id="inc-struct-01",
        incident_type="structural",
        drone_image_bytes=b"fake_image_data"
    )
    res_state = await supervisor.run(state)
    assert "VISION_AGENT" in res_state.assumptions[0]


@pytest.mark.asyncio
async def test_vision_agent_wrapper():
    """5. Test Vision Agent status labeling (REAL_MODEL_RESULT vs UNAVAILABLE)."""
    vision_agent = VisionAgent()
    
    # Test unavailable case when no image is provided
    state_no_img = CrisisState(incident_id="v1", incident_type="flood")
    res_no_img = await vision_agent.run(state_no_img)
    assert res_no_img.vision_analysis["status"] == "UNAVAILABLE"
    assert res_no_img.vision_analysis["damage_severity"] == 0.0


@pytest.mark.asyncio
async def test_intelligence_agent_wrapper():
    """6. Test Emergency Intelligence Agent text analysis wrapper."""
    intel_agent = EmergencyIntelligenceAgent()
    state = CrisisState(
        incident_id="nlp-1",
        incident_type="flood",
        emergency_text_reports=[
            {"text": "URGENT: 4 people trapped in flooded basement near Main St St", "source": "911_call"}
        ]
    )
    res = await intel_agent.run(state)
    assert len(res.emergency_reports) == 1
    assert res.emergency_reports[0]["is_urgent"] is True


@pytest.mark.asyncio
async def test_risk_agent_wrapper():
    """7. Test Risk Agent terminology and modeled survival-risk indicators."""
    risk_agent = RiskAssessmentAgent()
    state = CrisisState(
        incident_id="risk-1",
        incident_type="flood",
        priority_zones=[
            {"id": "00000000-0000-0000-0000-000000000001", "name": "Zone A", "population": 10000, "damage_score": 80.0}
        ]
    )
    res = await risk_agent.run(state)
    assert res.risk_assessment is not None
    top_zone = res.priority_zones[0]
    assert "modeled_survival_risk_indicator" in top_zone
    assert "priority_score" in top_zone
    assert any("modeled survival-risk indicator" in a for a in res.assumptions)


@pytest.mark.asyncio
async def test_response_planner_agent():
    """8. Test Response Planner Agent proposal generation."""
    planner = ResponsePlannerAgent()
    state = CrisisState(
        incident_id="plan-1",
        incident_type="flood",
        priority_zones=[
            {"zone_id": "00000000-0000-0000-0000-000000000001", "zone_name": "Zone A", "category": "RED", "population": 10000, "damage_severity": 85.0}
        ]
    )
    res = await planner.run(state)
    assert res.response_plan is not None
    assert res.response_plan["status"] == "PROPOSED"
    items = res.response_plan["priority_action_items"]
    assert len(items) == 1
    assert "reasoning" in items[0]
    assert "dependencies" in items[0]


@pytest.mark.asyncio
async def test_complete_phase1_graph():
    """9. Test complete Phase 1 Graph execution pipeline."""
    workflow = get_crisis_workflow()
    state = CrisisState(
        incident_id="phase1-graph-demo",
        incident_type="flood",
        title="Vijayawada Urban Flood Emergency",
        emergency_text_reports=[{"text": "Trapped people near downtown", "source": "call"}]
    )
    final_state = await workflow.execute(state)
    assert final_state.workflow_status in ["COMPLETED", "NEEDS_HUMAN_APPROVAL", "AWAITING_HUMAN_APPROVAL"]
    assert len(final_state.agent_history) >= 4
    assert final_state.response_plan is not None


@pytest.mark.asyncio
async def test_ollama_offline_fallback():
    """10. Test Scenario D: Ollama LLM offline fallback (app must not crash)."""
    provider = get_llm_provider()
    # Force invalid URL to test fallback
    provider.ollama_base_url = "http://localhost:9999"
    
    text_result = await provider.generate_text("Test prompt")
    assert text_result is None  # Gracefully returns None without crashing
    
    health = await provider.check_health()
    assert health["status"] == "unavailable"
    assert health["mode"] == "DETERMINISTIC_FALLBACK"


async def run_phase1_verification():
    """Run all Phase 1 tests synchronously."""
    print("==================================================")
    print(" CRISISMIND AI PHASE 1 VERIFICATION SUITE")
    print("==================================================")

    print("[TEST 1/10] CrisisState Initialization...")
    await test_crisis_state_initialization()
    print("  --> PASS")

    print("[TEST 2/10] Supervisor Routing (Flood)...")
    await test_supervisor_routing_flood()
    print("  --> PASS")

    print("[TEST 3/10] Supervisor Routing (Text-Only)...")
    await test_supervisor_routing_text_only()
    print("  --> PASS")

    print("[TEST 4/10] Supervisor Routing (Structural Image)...")
    await test_supervisor_routing_structural_image()
    print("  --> PASS")

    print("[TEST 5/10] Vision Agent Wrapper...")
    await test_vision_agent_wrapper()
    print("  --> PASS")

    print("[TEST 6/10] Emergency Intelligence Agent Wrapper...")
    await test_intelligence_agent_wrapper()
    print("  --> PASS")

    print("[TEST 7/10] Risk Assessment Agent Wrapper...")
    await test_risk_agent_wrapper()
    print("  --> PASS")

    print("[TEST 8/10] Response Planner Agent Wrapper...")
    await test_response_planner_agent()
    print("  --> PASS")

    print("[TEST 9/10] Complete Phase 1 Graph Execution...")
    await test_complete_phase1_graph()
    print("  --> PASS")

    print("[TEST 10/10] Scenario D: Ollama Offline Fallback...")
    await test_ollama_offline_fallback()
    print("  --> PASS")

    print("==================================================")
    print(" ALL 10 PHASE 1 VERIFICATION TESTS PASSED CLEANLY!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_phase1_verification())
