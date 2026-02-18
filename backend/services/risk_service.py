"""Risk scoring and assessment service."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np

from app.config import get_settings
from app.schemas import RiskMetrics, ZoneRiskAssessment

settings = get_settings()


class RiskScoringService:
    """Service for calculating risk scores and threat assessments."""
    
    # Weight factors for damage severity calculation
    DAMAGE_WEIGHTS = {
        "building_damage": 0.40,
        "infrastructure_damage": 0.30,
        "environmental_damage": 0.20,
        "accessibility": 0.10,
    }
    
    # Weight factors for survival probability
    SURVIVAL_WEIGHTS = {
        "time_factor": 0.35,
        "damage_factor": 0.25,
        "population_density": 0.20,
        "resource_proximity": 0.20,
    }
    
    # Time decay for survival (golden hour concept)
    GOLDEN_HOUR_MINUTES = 60
    CRITICAL_HOUR_MINUTES = 240  # 4 hours
    
    def __init__(self):
        pass
    
    def calculate_zone_risk(
        self,
        zone_data: Dict[str, Any],
        incident_data: Dict[str, Any],
        sensor_data: Optional[List[Dict]] = None,
        analysis_results: Optional[List[Dict]] = None
    ) -> ZoneRiskAssessment:
        """Calculate comprehensive risk assessment for a zone.
        
        Args:
            zone_data: Zone information (population, coordinates, etc.)
            incident_data: Incident details
            sensor_data: List of sensor readings
            analysis_results: List of AI analysis results
            
        Returns:
            ZoneRiskAssessment with metrics and factors
        """
        # Calculate damage severity
        damage_severity = self._calculate_damage_severity(
            zone_data, analysis_results, sensor_data
        )
        
        # Calculate survival probability
        survival_probability = self._calculate_survival_probability(
            zone_data, incident_data, damage_severity
        )
        
        # Determine threat level
        threat_level = self._classify_threat_level(
            damage_severity, 
            survival_probability,
            zone_data,
            sensor_data
        )
        
        # Calculate priority score for response
        priority_score = self._calculate_priority_score(
            damage_severity,
            survival_probability,
            threat_level,
            zone_data
        )
        
        # Compile factors breakdown
        factors = {
            "building_damage_contribution": damage_severity * self.DAMAGE_WEIGHTS["building_damage"],
            "infrastructure_contribution": damage_severity * self.DAMAGE_WEIGHTS["infrastructure_damage"],
            "time_decay_factor": self._calculate_time_decay(incident_data.get("started_at")),
            "population_at_risk": zone_data.get("population", 0),
            "sensor_anomaly_count": len([s for s in (sensor_data or []) if s.get("is_anomaly")]),
        }
        
        return ZoneRiskAssessment(
            zone_id=zone_data.get("id"),
            metrics=RiskMetrics(
                damage_severity=round(damage_severity, 2),
                survival_probability=round(survival_probability, 2),
                threat_level=threat_level,
                priority_score=round(priority_score, 2)
            ),
            factors=factors
        )
    
    def _calculate_damage_severity(
        self,
        zone_data: Dict[str, Any],
        analysis_results: Optional[List[Dict]],
        sensor_data: Optional[List[Dict]]
    ) -> float:
        """Calculate overall damage severity score (0-100)."""
        scores = []
        
        # From AI image analysis
        if analysis_results:
            for result in analysis_results:
                if result.get("analysis_type") == "image":
                    scores.append(result.get("results", {}).get("damage_score", 0))
        
        # From sensor data
        if sensor_data:
            for sensor in sensor_data:
                if sensor.get("is_anomaly"):
                    # Scale anomaly to damage contribution
                    anomaly_score = min(sensor.get("anomaly_score", 0) * 100, 100)
                    scores.append(anomaly_score)
        
        # From zone's own damage score if available
        if zone_data.get("damage_score"):
            scores.append(zone_data["damage_score"])
        
        if scores:
            # Weighted average - give more weight to AI analysis
            return min(np.mean(scores), 100)
        
        return 0.0
    
    def _calculate_survival_probability(
        self,
        zone_data: Dict[str, Any],
        incident_data: Dict[str, Any],
        damage_severity: float
    ) -> float:
        """Calculate survival probability (0-100)."""
        factors = []
        
        # Time factor (golden hour decay)
        time_factor = self._calculate_time_factor(incident_data.get("started_at"))
        factors.append(time_factor * self.SURVIVAL_WEIGHTS["time_factor"])
        
        # Damage factor (inverse relationship)
        damage_factor = max(0, 100 - damage_severity) / 100
        factors.append(damage_factor * self.SURVIVAL_WEIGHTS["damage_factor"])
        
        # Population density factor (higher density = harder to rescue)
        population = zone_data.get("population", 0)
        density_factor = max(0, 1 - (population / 50000))  # Normalize
        factors.append(density_factor * self.SURVIVAL_WEIGHTS["population_density"])
        
        # Resource proximity (assume 100% if not specified)
        resource_factor = 1.0
        factors.append(resource_factor * self.SURVIVAL_WEIGHTS["resource_proximity"])
        
        # Calculate weighted probability
        survival_prob = sum(factors) * 100
        
        return min(max(survival_prob, 0), 100)
    
    def _calculate_time_factor(self, started_at: Optional[datetime]) -> float:
        """Calculate time decay factor based on incident start time."""
        if started_at is None:
            return 1.0  # Assume recent if no time
        
        elapsed_minutes = (datetime.utcnow() - started_at).total_seconds() / 60
        
        if elapsed_minutes < self.GOLDEN_HOUR_MINUTES:
            # Within golden hour - minimal decay
            return 1.0 - (elapsed_minutes / self.GOLDEN_HOUR_MINUTES) * 0.2
        elif elapsed_minutes < self.CRITICAL_HOUR_MINUTES:
            # Between golden hour and critical hour
            progress = (elapsed_minutes - self.GOLDEN_HOUR_MINUTES) / (
                self.CRITICAL_HOUR_MINUTES - self.GOLDEN_HOUR_MINUTES
            )
            return 0.8 - progress * 0.3
        else:
            # Beyond critical hour
            return max(0.3, 0.5 - (elapsed_minutes - self.CRITICAL_HOUR_MINUTES) / 1000)
    
    def _calculate_time_decay(self, started_at: Optional[datetime]) -> float:
        """Calculate time decay as a factor (0-1)."""
        factor = self._calculate_time_factor(started_at)
        return round(1 - factor, 3)
    
    def _classify_threat_level(
        self,
        damage_severity: float,
        survival_probability: float,
        zone_data: Dict[str, Any],
        sensor_data: Optional[List[Dict]]
    ) -> str:
        """Classify overall threat level."""
        # Calculate composite score
        composite = (
            damage_severity * 0.4 +
            (100 - survival_probability) * 0.3 +
            self._get_sensor_threat_contribution(sensor_data) * 0.3
        )
        
        # Apply population multiplier
        population = zone_data.get("population", 0)
        if population > 10000:
            composite *= 1.1
        
        # Classify
        if composite >= settings.RISK_THRESHOLD_CRITICAL * 100:
            return "critical"
        elif composite >= settings.RISK_THRESHOLD_HIGH * 100:
            return "high"
        elif composite >= settings.RISK_THRESHOLD_MEDIUM * 100:
            return "medium"
        else:
            return "low"
    
    def _get_sensor_threat_contribution(
        self, 
        sensor_data: Optional[List[Dict]]
    ) -> float:
        """Calculate threat contribution from sensor anomalies."""
        if not sensor_data:
            return 0.0
        
        anomaly_count = len([s for s in sensor_data if s.get("is_anomaly")])
        return min(anomaly_count * 20, 100)  # Each anomaly adds 20 points
    
    def _calculate_priority_score(
        self,
        damage_severity: float,
        survival_probability: float,
        threat_level: str,
        zone_data: Dict[str, Any]
    ) -> float:
        """Calculate response priority score."""
        # Base score from threat level
        threat_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        base_score = threat_scores.get(threat_level, 0)
        
        # Adjust based on population
        population = zone_data.get("population", 0)
        population_multiplier = min(1 + (population / 50000), 1.5)
        
        # Adjust based on survival probability (lower = higher priority)
        survival_factor = (100 - survival_probability) / 100
        
        priority = base_score * population_multiplier * (1 + survival_factor)
        return min(priority, 100)
    
    def prioritize_zones(
        self, 
        zone_assessments: List[ZoneRiskAssessment]
    ) -> List[ZoneRiskAssessment]:
        """Sort zones by priority score (highest first)."""
        return sorted(
            zone_assessments,
            key=lambda x: x.metrics.priority_score,
            reverse=True
        )
    
    def calculate_overall_incident_risk(
        self,
        zone_assessments: List[ZoneRiskAssessment]
    ) -> Dict[str, Any]:
        """Calculate overall risk metrics for an incident."""
        if not zone_assessments:
            return {
                "average_damage": 0,
                "average_survival": 100,
                "critical_zones": 0,
                "high_risk_zones": 0,
                "overall_threat": "low"
            }
        
        avg_damage = np.mean([z.metrics.damage_severity for z in zone_assessments])
        avg_survival = np.mean([z.metrics.survival_probability for z in zone_assessments])
        critical_zones = len([z for z in zone_assessments if z.metrics.threat_level == "critical"])
        high_risk_zones = len([z for z in zone_assessments if z.metrics.threat_level == "high"])
        
        # Overall threat level
        if critical_zones > 0:
            overall_threat = "critical"
        elif high_risk_zones > 1:
            overall_threat = "high"
        elif high_risk_zones == 1:
            overall_threat = "medium"
        else:
            overall_threat = "low"
        
        return {
            "average_damage": round(avg_damage, 2),
            "average_survival": round(avg_survival, 2),
            "critical_zones": critical_zones,
            "high_risk_zones": high_risk_zones,
            "overall_threat": overall_threat,
            "total_zones": len(zone_assessments)
        }


# Singleton instance
_risk_service: Optional[RiskScoringService] = None


def get_risk_service() -> RiskScoringService:
    """Get or create risk scoring service singleton."""
    global _risk_service
    if _risk_service is None:
        _risk_service = RiskScoringService()
    return _risk_service
