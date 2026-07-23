import asyncio
import os
import sys

# Set offline transformer flag for fast unit tests
os.environ["SKIP_TRANSFORMER_DOWNLOAD"] = "1"

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.main import app, active_crisis_states
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_system_mode_endpoint():
    """1. Test system mode status endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        resp = await client.get("/api/v1/system/mode")
        assert resp.status_code == 200
        data = resp.json()
        assert data["active_mode"] == "LIVE_INTELLIGENCE_READY"
        assert "SIMULATION_MODE" in data["modes_supported"]
        assert "LIVE_INTELLIGENCE_MODE" in data["modes_supported"]
        print("  --> PASS: System Mode Endpoint")


@pytest.mark.asyncio
async def test_live_incident_analysis():
    """2. Test live incident analysis execution for custom user real coordinates."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {
            "incident_type": "flood",
            "title": "Visakhapatnam Cyclone & Inundation",
            "latitude": 17.6868,
            "longitude": 83.2185,
            "emergency_text": "Heavy rainfall caused coastal inundation near harbour road.",
            "available_resources": {"rescue_teams": 5, "ambulances": 8, "rescue_boats": 4}
        }
        resp = await client.post("/api/v1/incidents/live-analysis", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["incident_id"] is not None
        assert data["workflow_status"] in ["AWAITING_HUMAN_APPROVAL", "COMPLETED", "HUMAN_REVIEW_REQUIRED"]
        assert data["is_simulation"] is False
        assert data["location"]["latitude"] == 17.6868
        assert data["location"]["longitude"] == 83.2185
        assert len(data["agent_history"]) >= 4
        print("  --> PASS: Live Incident Analysis Multi-Agent Execution")


async def run_phase5_verification():
    print("=" * 50)
    print(" CRISISMIND AI PHASE 5 DUAL-MODE VERIFICATION")
    print("=" * 50)
    print("[TEST 1/2] System Operational Dual-Mode Status Endpoint...")
    await test_system_mode_endpoint()
    print("[TEST 2/2] Live Incident Analysis Multi-Agent Execution...")
    await test_live_incident_analysis()
    print("=" * 50)
    print(" ALL PHASE 5 DUAL-MODE TESTS PASSED CLEANLY!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_phase5_verification())
