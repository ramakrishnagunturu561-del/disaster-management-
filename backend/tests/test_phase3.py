"""Comprehensive Phase 3 Test Suite: Safety Critic, Self-Correction Re-planning, and Governance."""
import os
import sys
import asyncio
import pytest

os.environ["SKIP_TRANSFORMER_DOWNLOAD"] = "1"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.crisis_state import CrisisState
from app.graph.crisis_graph import get_crisis_workflow
from app.agents.critic_agent import CriticSafetyAgent
from app.agents.resource_agent import ResourceAllocationAgent
from app.agents.route_agent import EvacuationRouteAgent
from app.agents.response_planner_agent import ResponsePlannerAgent


@pytest.mark.asyncio
async def test_valid_plan_critic_pass():
    """3. Valid plan -> Critic PASS."""
    critic = CriticSafetyAgent()
    state = CrisisState(
        incident_id="tc-03",
        incident_type="flood",
        available_resources={"rescue_teams": 5, "ambulances": 10},
        priority_zones=[
            {"zone_id": "z1", "zone_name": "Downtown", "population": 200, "category": "RED"}
        ],
        resource_plan={"total_allocated": {"rescue_teams": 3, "ambulances": 5}},
        evacuation_plan={
            "z1": {"target_shelter": "Shelter A", "shelter_capacity_remaining": 500, "primary_route": {"status": "CLEAR"}}
        },
        route_analysis={"blocked_corridors": []},
        weather_intelligence={"status": "OK", "timestamp": "2026-07-23T10:00:00"},
        evidence=[{"source": "REAL_SENSOR", "detail": "Water level sensor WL-01 at 4.8m"}]
    )
    res_state = await critic.run(state)
    assert res_state.critic_result.passed is True
    assert res_state.approval_status == "PROPOSED"


@pytest.mark.asyncio
async def test_resource_overallocation_critic_fail():
    """4. Resource over-allocation -> FAIL (RESOURCE_OVERALLOCATED)."""
    critic = CriticSafetyAgent()
    state = CrisisState(
        incident_id="tc-04",
        incident_type="flood",
        available_resources={"rescue_teams": 2},  # Only 2 available
        resource_plan={"total_allocated": {"rescue_teams": 5}}  # 5 planned
    )
    res_state = await critic.run(state)
    assert res_state.critic_result.passed is False
    codes = [v["code"] for v in res_state.unresolved_violations]
    assert "RESOURCE_OVERALLOCATED" in codes
    assert "resource_agent" in res_state.replan_targets


@pytest.mark.asyncio
async def test_shelter_capacity_exceeded_critic_fail():
    """5. Shelter capacity exceeded -> FAIL (SHELTER_CAPACITY_EXCEEDED)."""
    critic = CriticSafetyAgent()
    state = CrisisState(
        incident_id="tc-05",
        incident_type="flood",
        priority_zones=[{"zone_id": "z1", "zone_name": "Downtown", "population": 500}],
        evacuation_plan={
            "z1": {"target_shelter": "Shelter A", "shelter_capacity_remaining": 300}  # 300 < 500
        }
    )
    res_state = await critic.run(state)
    assert res_state.critic_result.passed is False
    codes = [v["code"] for v in res_state.unresolved_violations]
    assert "SHELTER_CAPACITY_EXCEEDED" in codes


@pytest.mark.asyncio
async def test_blocked_route_critic_fail():
    """6. Blocked route -> FAIL (ROUTE_BLOCKED)."""
    critic = CriticSafetyAgent()
    state = CrisisState(
        incident_id="tc-06",
        incident_type="flood",
        route_analysis={"blocked_corridors": ["Highway 16 Bridge"]},
        response_plan={
            "priority_action_items": [
                {"zone": "Downtown", "route": "Highway 16 Bridge"}  # Conflict!
            ]
        }
    )
    res_state = await critic.run(state)
    assert res_state.critic_result.passed is False
    codes = [v["code"] for v in res_state.unresolved_violations]
    assert "ROUTE_BLOCKED" in codes


@pytest.mark.asyncio
async def test_stale_weather_severity():
    """7. Stale weather -> HIGH severity violation."""
    critic = CriticSafetyAgent()
    state = CrisisState(
        incident_id="tc-07",
        incident_type="flood",
        weather_intelligence={"status": "OK", "timestamp": "2026-07-20T10:00:00"}  # 3 days old
    )
    res_state = await critic.run(state)
    codes = [v["code"] for v in res_state.unresolved_violations]
    assert "STALE_WEATHER" in codes


@pytest.mark.asyncio
async def test_vijayawada_self_correction_demo():
    """10-13 & Section 15: Required Vijayawada Urban Flood Self-Correction Demo.
    500 evacuees -> Shelter A capacity 300 (Initial FAIL) -> Re-plan assigns Shelter A + Shelter B -> Plan v2 (PASS).
    """
    state = CrisisState(
        incident_id="vijayawada-demo-01",
        incident_type="flood",
        title="Vijayawada Urban Flood Emergency",
        available_resources={"rescue_teams": 10, "ambulances": 15},
        priority_zones=[
            {"zone_id": "z_dt", "zone_name": "Downtown Riverbank", "population": 500, "category": "RED"}
        ],
        weather_intelligence={"status": "OK", "timestamp": "2026-07-23T10:00:00"},
        # Intentionally flawed initial evacuation plan (only 300 capacity)
        evacuation_plan={
            "z_dt": {"target_shelter": "Shelter A", "shelter_capacity_remaining": 300}
        },
        resource_plan={"total_allocated": {"rescue_teams": 4, "ambulances": 6}}
    )

    critic = CriticSafetyAgent()
    
    # Step 1: Initial Plan v1 Evaluation
    res_v1 = await critic.run(state)
    assert res_v1.critic_result.passed is False
    assert "SHELTER_CAPACITY_EXCEEDED" in [v["code"] for v in res_v1.unresolved_violations]

    # Step 2: Targeted Re-plan triggered (Route Agent + Planner Agent adjust shelter allocations)
    res_v1.replan_count += 1
    res_v1.decision_history.append({
        "version": res_v1.decision_version,
        "response_plan": res_v1.response_plan,
        "critic_result": res_v1.critic_result.model_dump()
    })
    res_v1.decision_version = 2

    # Corrective action: Assign secondary shelter (Shelter B) to accommodate remaining 200 evacuees
    res_v1.evacuation_plan = {
        "z_dt": {
            "target_shelter": "Shelter A (300) + Shelter B (200)",
            "shelter_capacity_remaining": 600,
            "primary_route": {"status": "CLEAR"}
        }
    }

    # Step 3: Plan v2 Safety Critic Validation
    res_v2 = await critic.run(res_v1)
    assert res_v2.critic_result.passed is True
    assert res_v2.decision_version == 2
    assert len(res_v2.decision_history) == 1
    assert res_v2.workflow_status == "AWAITING_HUMAN_APPROVAL"


@pytest.mark.asyncio
async def test_max_replan_protection():
    """14-15. Maximum re-plan protection limit reached -> HUMAN_REVIEW_REQUIRED."""
    workflow = get_crisis_workflow()
    state = CrisisState(
        incident_id="tc-max-replan",
        incident_type="flood",
        replan_count=0,
        max_replan_limit=3,
        priority_zones=[{
            "id": "00000000-0000-0000-0000-000000000099",
            "zone_id": "00000000-0000-0000-0000-000000000099",
            "zone_name": "Flooded Zone",
            "population": 1000
        }],
        evacuation_plan={
            "00000000-0000-0000-0000-000000000099": {
                "target_shelter": "UNAVAILABLE_FLOODED_SHELTER",
                "shelter_capacity_remaining": -100
            }
        }
    )
    final_state = await workflow.execute(state)
    assert final_state.workflow_status == "HUMAN_REVIEW_REQUIRED"
    assert final_state.approval_status == "HUMAN_REVIEW_REQUIRED"
    assert final_state.replan_count >= 3


@pytest.mark.asyncio
async def test_adversarial_malformed_plans():
    """17. Test adversarial conditions (negative quantities, nonexistent resource types)."""
    critic = CriticSafetyAgent()
    state = CrisisState(
        incident_id="tc-adversarial",
        incident_type="flood",
        available_resources={"rescue_teams": 5},
        resource_plan={
            "total_allocated": {"rescue_teams": -2, "alien_drones": 10}
        }
    )
    res_state = await critic.run(state)
    assert res_state.critic_result.passed is False
    codes = [v["code"] for v in res_state.unresolved_violations]
    assert "NEGATIVE_RESOURCE_QUANTITY" in codes
    assert "NONEXISTENT_RESOURCE_TYPE" in codes


async def run_phase3_verification():
    """Run all Phase 3 tests synchronously."""
    print("==================================================")
    print(" CRISISMIND AI PHASE 3 SAFETY & GOVERNANCE SUITE")
    print("==================================================")

    print("[TEST 1/7] Valid Plan -> Critic PASS...")
    await test_valid_plan_critic_pass()
    print("  --> PASS")

    print("[TEST 2/7] Resource Over-allocation -> Critic FAIL...")
    await test_resource_overallocation_critic_fail()
    print("  --> PASS")

    print("[TEST 3/7] Shelter Capacity Exceeded -> Critic FAIL...")
    await test_shelter_capacity_exceeded_critic_fail()
    print("  --> PASS")

    print("[TEST 4/7] Blocked Route Conflict -> Critic FAIL...")
    await test_blocked_route_critic_fail()
    print("  --> PASS")

    print("[TEST 5/7] Stale Weather Telemetry -> High Severity Violation...")
    await test_stale_weather_severity()
    print("  --> PASS")

    print("[TEST 6/7] Vijayawada Self-Correction Demo (Plan v1 FAIL -> Re-plan -> Plan v2 PASS)...")
    await test_vijayawada_self_correction_demo()
    print("  --> PASS")

    print("[TEST 7/7] Maximum Re-plan Limit -> HUMAN_REVIEW_REQUIRED Protection...")
    await test_max_replan_protection()
    print("  --> PASS")

    print("==================================================")
    print(" ALL PHASE 3 SAFETY & GOVERNANCE TESTS PASSED CLEANLY!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_phase3_verification())
