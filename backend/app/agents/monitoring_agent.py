"""Continuous Monitoring Agent."""
import logging
from datetime import datetime
from typing import Dict, Any
from app.graph.crisis_state import CrisisState

logger = logging.getLogger(__name__)


class MonitoringAgent:
    """Agent responsible for continuously watching real-time sensor streams, weather updates, 
    and emergency telemetry to trigger autonomous reassessment when significant changes occur."""

    def __init__(self):
        self.name = "MONITORING_AGENT"

    async def run(self, state: CrisisState, new_event: Optional[Dict[str, Any]] = None) -> CrisisState:
        """Evaluate incoming live telemetric events for significant state changes."""
        state.record_step(
            agent=self.name,
            action="EVALUATE_STATE_CHANGE",
            status="STARTED",
            summary="Monitoring live disaster telemetry for significant operational changes."
        )

        significant_change = False
        change_reason = ""

        if new_event:
            etype = new_event.get("event_type", "").upper()
            if etype in ["SENSOR_CRITICAL", "NEW_IMAGE_UPLOAD", "SEVERE_WEATHER_ALERT", "MASS_CASUALTY_REPORT"]:
                significant_change = True
                change_reason = f"Significant telemetry change detected: {new_event.get('title', etype)}"

        if significant_change:
            state.workflow_status = "REASSESSING"
            state.warnings.append(f"Continuous Monitoring: {change_reason}. Triggering autonomous reassessment.")
            summary_msg = f"Significant change detected ({change_reason}). Re-routing to Incident Commander."
        else:
            summary_msg = "No significant operational threshold changes detected. Monitoring active."

        state.record_step(
            agent=self.name,
            action="EVALUATE_STATE_CHANGE",
            status="COMPLETED",
            summary=summary_msg,
            confidence=0.96
        )

        return state
