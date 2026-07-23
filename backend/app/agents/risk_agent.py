"""Risk Assessment Agent wrapping risk scoring service."""
import logging
from typing import Dict, Any, List
from app.graph.crisis_state import CrisisState
from services.risk_service import get_risk_service

logger = logging.getLogger(__name__)


class RiskAssessmentAgent:
    """Agent responsible for computing multi-factor priority scores, 
    modeled survival-risk indicators, and risk zone categorization (GREEN, YELLOW, RED, BLACK)."""

    def __init__(self):
        self.name = "RISK_AGENT"
        self.risk_service = get_risk_service()

    async def run(self, state: CrisisState) -> CrisisState:
        """Calculate comprehensive risk assessment across zones."""
        state.record_step(
            agent=self.name,
            action="CALCULATE_RISK_ASSESSMENT",
            status="STARTED",
            summary="Computing zone threat levels, priority scores, and modeled survival-risk indicators."
        )

        # Explicitly record methodology assumptions
        state.assumptions.extend([
            "Survival probability is calculated as a modeled survival-risk indicator based on Golden Hour time decay, not medical certainty.",
            "Population exposure counts reflect geographic census baseline estimates for targeted zones."
        ])

        # Prepare zone data inputs from current state
        zones = state.priority_zones if state.priority_zones else [
            {"id": "00000000-0000-0000-0000-00000000000a", "name": "Zone A - Riverfront / Downtown", "population": 14500, "damage_score": 75.0, "coordinates": [[16.50, 80.64], [16.51, 80.65]]},
            {"id": "00000000-0000-0000-0000-00000000000b", "name": "Zone B - Residential Heights", "population": 22000, "damage_score": 35.0, "coordinates": [[16.52, 80.66], [16.53, 80.67]]},
            {"id": "00000000-0000-0000-0000-00000000000c", "name": "Zone C - Industrial Park", "population": 4200, "damage_score": 88.0, "coordinates": [[16.49, 80.62], [16.50, 80.63]]}
        ]

        incident_data = {
            "id": state.incident_id,
            "started_at": None,
            "severity": 8
        }

        # Integrate vision results into zone damage scores
        if state.vision_analysis and state.vision_analysis.get("status") == "REAL_MODEL_RESULT":
            vis_score = state.vision_analysis.get("damage_severity", 0.0)
            if vis_score > 0:
                zones[0]["damage_score"] = vis_score

        assessed_zones = []
        total_population_exposed = 0

        for z in zones:
            assessment = self.risk_service.calculate_zone_risk(
                zone_data=z,
                incident_data=incident_data,
                sensor_data=state.sensor_readings,
                analysis_results=[state.vision_analysis] if state.vision_analysis else []
            )

            metrics = assessment.metrics
            # Map threat level to standard CrisisMind zone color categories
            threat_str = metrics.threat_level.lower()
            zone_category = (
                "BLACK" if threat_str == "critical" and metrics.damage_severity > 85 else
                "RED" if threat_str in ["critical", "high"] else
                "YELLOW" if threat_str == "medium" else
                "GREEN"
            )

            total_population_exposed += z.get("population", 0)

            assessed_zones.append({
                "zone_id": z.get("id"),
                "zone_name": z.get("name"),
                "population": z.get("population"),
                "category": zone_category,
                "threat_level": metrics.threat_level.upper(),
                "damage_severity": metrics.damage_severity,
                "modeled_survival_risk_indicator": metrics.survival_probability,
                "priority_score": metrics.priority_score,
                "factors": assessment.factors
            })

        # Sort priority zones by priority score descending
        assessed_zones.sort(key=lambda x: x["priority_score"], reverse=True)

        state.priority_zones = assessed_zones
        state.population_exposure = total_population_exposed
        state.risk_assessment = {
            "highest_threat_zone": assessed_zones[0]["zone_name"] if assessed_zones else "N/A",
            "critical_zone_count": len([z for z in assessed_zones if z["category"] in ["RED", "BLACK"]]),
            "total_population_at_risk": total_population_exposed,
            "overall_status": "HIGH_RISK" if any(z["category"] in ["RED", "BLACK"] for z in assessed_zones) else "MODERATE"
        }

        summary_text = (
            f"Risk calculation complete across {len(assessed_zones)} zones. "
            f"Top priority: {assessed_zones[0]['zone_name']} (Priority Score: {assessed_zones[0]['priority_score']:.1f}). "
            f"Total population exposed: {total_population_exposed:,}."
        )

        state.record_step(
            agent=self.name,
            action="CALCULATE_RISK_ASSESSMENT",
            status="COMPLETED",
            summary=summary_text,
            confidence=0.92
        )

        return state
