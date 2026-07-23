"""Standalone test runner for CrisisMind AI Multi-Agent suite."""
import asyncio
import os
import sys

os.environ["SKIP_TRANSFORMER_DOWNLOAD"] = "1"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.crisis_state import CrisisState
from app.graph.crisis_graph import CrisisMindWorkflow
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.resource_agent import ResourceAllocationAgent
from app.agents.critic_agent import CriticSafetyAgent


async def run_all_tests():
    print("==================================================")
    print(" RUNNING CRISISMIND AI MULTI-AGENT VERIFICATION")
    print("==================================================")

    # Test 1: Supervisor Agent
    print("[TEST 1/5] Testing Supervisor Agent Routing...")
    supervisor = SupervisorAgent()
    state1 = CrisisState(incident_id="t1", incident_type="flood")
    res1 = await supervisor.run(state1)
    assert res1.current_agent == "INCIDENT_COMMANDER", "Supervisor failed to update current_agent"
    assert len(res1.agent_history) >= 1, "Agent history step missing"
    print("  --> PASS: Supervisor Agent correctly classified incident and set routing pipeline.")

    # Test 2: Risk Agent
    print("[TEST 2/5] Testing Risk Assessment Agent...")
    risk_agent = RiskAssessmentAgent()
    state2 = CrisisState(incident_id="t2", incident_type="flood", priority_zones=[{"id": "00000000-0000-0000-0000-000000000001", "name": "Downtown", "population": 15000, "damage_score": 85.0}])
    res2 = await risk_agent.run(state2)
    assert res2.risk_assessment is not None, "Risk assessment object missing"
    assert "modeled_survival_risk_indicator" in res2.priority_zones[0], "Modeled survival indicator missing"
    print(f"  --> PASS: Risk Assessment completed. Priority Score: {res2.priority_zones[0]['priority_score']:.1f}, Threat: {res2.priority_zones[0]['threat_level']}.")

    # Test 3: Resource Constraint Validation
    print("[TEST 3/5] Testing Resource Allocation Constraints...")
    resource_agent = ResourceAllocationAgent()
    state3 = CrisisState(incident_id="t3", incident_type="flood", available_resources={"rescue_teams": 3}, priority_zones=[{"zone_id": "z1", "category": "RED"}])
    res3 = await resource_agent.run(state3)
    totals = res3.resource_plan["total_allocated"]
    assert totals["rescue_teams"] <= 3, "Resource over-allocation constraint violated!"
    print("  --> PASS: Resource Agent enforced strict availability constraints (Allocated <= Available).")

    # Test 4: Critic Safety Agent
    print("[TEST 4/5] Testing Critic Safety Agent PASS / FAIL Detection...")
    critic = CriticSafetyAgent()
    # Test pass case
    state4_pass = CrisisState(incident_id="t4", incident_type="flood", available_resources={"rescue_teams": 10}, resource_plan={"initial_inventory": {"rescue_teams": 10}, "total_allocated": {"rescue_teams": 5}})
    res4_pass = await critic.run(state4_pass)
    assert res4_pass.critic_result.passed is True, "Critic failed valid plan!"

    # Test fail case
    state4_fail = CrisisState(incident_id="t4b", incident_type="flood", available_resources={"rescue_teams": 5}, resource_plan={"initial_inventory": {"rescue_teams": 5}, "total_allocated": {"rescue_teams": 12}})
    res4_fail = await critic.run(state4_fail)
    assert res4_fail.critic_result.passed is False, "Critic missed invalid over-allocation!"
    print("  --> PASS: Critic Safety Agent correctly passed valid plan and rejected over-allocated plan.")

    # Test 5: Full Workflow Execution
    print("[TEST 5/5] Testing Full Multi-Agent Graph State Machine...")
    workflow = CrisisMindWorkflow()
    state5 = CrisisState(incident_id="vijayawada-demo", incident_type="flood", title="Vijayawada Flood Emergency")
    final_state = await workflow.execute(state5)
    assert final_state.workflow_status in ["COMPLETED", "NEEDS_HUMAN_APPROVAL"], f"Unexpected status {final_state.workflow_status}"
    assert len(final_state.agent_history) >= 10, "Execution steps incomplete"
    print(f"  --> PASS: Multi-Agent Workflow Executed {len(final_state.agent_history)} steps. Final Workflow Status: {final_state.workflow_status}.")

    print("==================================================")
    print(" ALL 5 MULTI-AGENT VERIFICATION TESTS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
