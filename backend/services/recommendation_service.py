"""Recommendation engine for response strategies."""
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import get_settings
from app.models import RiskLevel, ResourceType

settings = get_settings()


class RecommendationService:
    """Service for generating AI-powered response recommendations."""
    
    # Response templates by category
    RESPONSE_TEMPLATES = {
        "rescue": {
            "critical": {
                "title": "Immediate Search & Rescue Deployment",
                "description": "Deploy {count} heavy rescue teams with structural collapse equipment to {zone}. Estimated {casualties} casualties requiring extraction.",
                "resources": [ResourceType.RESCUE_TEAM],
            },
            "high": {
                "title": "Deploy Rescue Assessment Team",
                "description": "Send {count} rescue teams to {zone} for damage assessment and victim location.",
                "resources": [ResourceType.RESCUE_TEAM],
            },
        },
        "medical": {
            "critical": {
                "title": "Emergency Medical Response Required",
                "description": "Deploy {count} ambulances and medical teams to {zone}. High casualty count expected.",
                "resources": [ResourceType.AMBULANCE],
            },
            "high": {
                "title": "Medical Standby Alert",
                "description": "Position {count} ambulances near {zone} for rapid response.",
                "resources": [ResourceType.AMBULANCE],
            },
        },
        "evacuation": {
            "critical": {
                "title": "Mandatory Evacuation Order",
                "description": "Initiate immediate evacuation of {zone}. Estimated {population} people at critical risk.",
                "resources": [],
            },
            "high": {
                "title": "Prepare Evacuation Routes",
                "description": "Clear and secure evacuation routes from {zone}. Alert transportation resources.",
                "resources": [],
            },
        },
        "surveillance": {
            "critical": {
                "title": "Continuous Aerial Surveillance",
                "description": "Deploy {count} drones for 24/7 monitoring of {zone}. Critical infrastructure at risk.",
                "resources": [ResourceType.DRONE],
            },
            "high": {
                "title": "Deploy Drone Survey Team",
                "description": "Send {count} drones to assess damage extent in {zone}.",
                "resources": [ResourceType.DRONE],
            },
        },
        "fire": {
            "critical": {
                "title": "Major Fire Suppression Required",
                "description": "Deploy {count} fire units with heavy equipment to {zone}. Fire spreading risk high.",
                "resources": [ResourceType.FIRE_TRUCK],
            },
            "high": {
                "title": "Fire Containment Response",
                "description": "Position {count} fire units at {zone} perimeter.",
                "resources": [ResourceType.FIRE_TRUCK],
            },
        },
    }
    
    def __init__(self):
        pass
    
    def generate_recommendations(
        self,
        zone_data: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        available_resources: Dict[str, int],
        incident_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations for a zone.
        
        Args:
            zone_data: Zone information
            risk_metrics: Risk assessment metrics
            available_resources: Count of available resources by type
            incident_context: Additional incident context
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        threat_level = risk_metrics.get("threat_level", "low")
        damage_severity = risk_metrics.get("damage_severity", 0)
        survival_prob = risk_metrics.get("survival_probability", 100)
        
        # Critical threat recommendations
        if threat_level == "critical":
            recommendations.extend(self._generate_critical_recommendations(
                zone_data, risk_metrics, available_resources
            ))
        
        # High threat recommendations
        elif threat_level == "high":
            recommendations.extend(self._generate_high_recommendations(
                zone_data, risk_metrics, available_resources
            ))
        
        # Medium threat recommendations
        elif threat_level == "medium":
            recommendations.extend(self._generate_medium_recommendations(
                zone_data, risk_metrics, available_resources
            ))
        
        # Sort by priority
        recommendations.sort(key=lambda x: self._priority_value(x["priority"]), reverse=True)
        
        return recommendations
    
    def _generate_critical_recommendations(
        self,
        zone_data: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        available_resources: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for critical threat level."""
        recommendations = []
        zone_name = zone_data.get("name", "Zone")
        population = zone_data.get("population", 0)
        
        # Rescue recommendation
        if available_resources.get("rescue_team", 0) > 0:
            count = min(3, available_resources["rescue_team"])
            rec = self._create_recommendation(
                category="rescue",
                priority="critical",
                zone_name=zone_name,
                count=count,
                population=population,
                casualties=int(population * 0.05)  # Estimate 5% casualties
            )
            recommendations.append(rec)
        
        # Medical recommendation
        if available_resources.get("ambulance", 0) > 0:
            count = min(5, available_resources["ambulance"])
            rec = self._create_recommendation(
                category="medical",
                priority="critical",
                zone_name=zone_name,
                count=count,
                population=population
            )
            recommendations.append(rec)
        
        # Evacuation recommendation
        if population > 1000:
            rec = self._create_recommendation(
                category="evacuation",
                priority="critical",
                zone_name=zone_name,
                count=0,
                population=population
            )
            recommendations.append(rec)
        
        # Surveillance recommendation
        if available_resources.get("drone", 0) > 0:
            count = min(2, available_resources["drone"])
            rec = self._create_recommendation(
                category="surveillance",
                priority="critical",
                zone_name=zone_name,
                count=count,
                population=population
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_high_recommendations(
        self,
        zone_data: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        available_resources: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for high threat level."""
        recommendations = []
        zone_name = zone_data.get("name", "Zone")
        population = zone_data.get("population", 0)
        
        # Rescue assessment
        if available_resources.get("rescue_team", 0) > 0:
            count = min(2, available_resources["rescue_team"])
            rec = self._create_recommendation(
                category="rescue",
                priority="high",
                zone_name=zone_name,
                count=count,
                population=population
            )
            recommendations.append(rec)
        
        # Medical standby
        if available_resources.get("ambulance", 0) > 0:
            count = min(2, available_resources["ambulance"])
            rec = self._create_recommendation(
                category="medical",
                priority="high",
                zone_name=zone_name,
                count=count,
                population=population
            )
            recommendations.append(rec)
        
        # Drone survey
        if available_resources.get("drone", 0) > 0:
            count = min(1, available_resources["drone"])
            rec = self._create_recommendation(
                category="surveillance",
                priority="high",
                zone_name=zone_name,
                count=count,
                population=population
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_medium_recommendations(
        self,
        zone_data: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        available_resources: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for medium threat level."""
        recommendations = []
        zone_name = zone_data.get("name", "Zone")
        
        # Basic monitoring
        if available_resources.get("drone", 0) > 0:
            rec = self._create_recommendation(
                category="surveillance",
                priority="medium",
                zone_name=zone_name,
                count=1,
                population=0
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _create_recommendation(
        self,
        category: str,
        priority: str,
        zone_name: str,
        count: int,
        population: int,
        casualties: int = 0
    ) -> Dict[str, Any]:
        """Create a recommendation dictionary."""
        template = self.RESPONSE_TEMPLATES.get(category, {}).get(priority, {})
        
        title = template.get("title", f"{category.title()} Response")
        description_template = template.get("description", "Deploy resources to {zone}.")
        
        description = description_template.format(
            count=count,
            zone=zone_name,
            population=population,
            casualties=casualties
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            category, priority, zone_name, population, casualties
        )
        
        return {
            "category": category,
            "priority": priority,
            "title": title,
            "description": description,
            "reasoning": reasoning,
            "resources_required": template.get("resources", []),
            "estimated_impact": self._estimate_impact(category, count, population),
            "time_sensitivity": "immediate" if priority == "critical" else "urgent" if priority == "high" else "normal"
        }
    
    def _generate_reasoning(
        self,
        category: str,
        priority: str,
        zone_name: str,
        population: int,
        casualties: int
    ) -> str:
        """Generate AI explanation for the recommendation."""
        reasoning_parts = []
        
        # Threat level reasoning
        if priority == "critical":
            reasoning_parts.append(
                f"AI analysis identified CRITICAL threat level in {zone_name}. "
                f"Multiple risk factors exceed safety thresholds."
            )
        elif priority == "high":
            reasoning_parts.append(
                f"Elevated risk detected in {zone_name} requiring proactive response."
            )
        
        # Population impact
        if population > 5000:
            reasoning_parts.append(
                f"Large population of {population:,} people at risk."
            )
        
        # Casualty estimate
        if casualties > 0:
            reasoning_parts.append(
                f"Estimated {casualties} casualties requiring immediate attention."
            )
        
        # Category-specific reasoning
        category_reasoning = {
            "rescue": "Structural damage indicators suggest trapped individuals. Thermal imaging analysis supports rescue deployment.",
            "medical": "Casualty projections exceed local medical capacity. Pre-positioning resources will reduce response time.",
            "evacuation": "Environmental hazards present ongoing risk. Evacuation will prevent additional casualties.",
            "surveillance": "Continuous monitoring required for situational awareness and secondary hazard detection.",
            "fire": "Fire propagation models indicate spreading risk. Early containment prevents escalation."
        }
        
        if category in category_reasoning:
            reasoning_parts.append(category_reasoning[category])
        
        return " ".join(reasoning_parts)
    
    def _estimate_impact(
        self,
        category: str,
        resource_count: int,
        population: int
    ) -> Dict[str, Any]:
        """Estimate the impact of executing the recommendation."""
        impact_multipliers = {
            "rescue": 15,  # People rescued per team
            "medical": 5,  # People treated per ambulance
            "evacuation": 100,  # People evacuated per operation
            "surveillance": 0,  # Informational
            "fire": 50,  # People protected
        }
        
        multiplier = impact_multipliers.get(category, 1)
        estimated_lives_saved = resource_count * multiplier
        
        return {
            "estimated_lives_saved": estimated_lives_saved,
            "estimated_lives_improved": int(population * 0.1) if category == "evacuation" else 0,
            "resource_cost": resource_count,
            "time_to_effectiveness": "15-30 minutes" if category in ["rescue", "medical"] else "1-2 hours"
        }
    
    def _priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value for sorting."""
        return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(priority, 0)
    
    def optimize_resource_allocation(
        self,
        zones: List[Dict[str, Any]],
        available_resources: Dict[str, int],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Optimize resource allocation across multiple zones.
        
        Returns:
            Dictionary mapping zone_id to list of allocated resources
        """
        allocation = {}
        remaining_resources = available_resources.copy()
        
        # Sort zones by priority score
        sorted_zones = sorted(
            zones,
            key=lambda z: z.get("priority_score", 0),
            reverse=True
        )
        
        for zone in sorted_zones:
            zone_id = zone.get("id")
            zone_allocation = []
            
            # Allocate based on threat level
            threat = zone.get("threat_level", "low")
            
            if threat == "critical":
                # Maximize resources for critical zones
                for resource_type, count in remaining_resources.items():
                    allocate = min(count, 3)  # Max 3 per type
                    if allocate > 0:
                        zone_allocation.append({
                            "type": resource_type,
                            "count": allocate
                        })
                        remaining_resources[resource_type] -= allocate
            
            elif threat == "high":
                # Moderate allocation
                for resource_type, count in remaining_resources.items():
                    allocate = min(count, 2)
                    if allocate > 0:
                        zone_allocation.append({
                            "type": resource_type,
                            "count": allocate
                        })
                        remaining_resources[resource_type] -= allocate
            
            allocation[zone_id] = zone_allocation
        
        return allocation


# Singleton instance
_rec_service: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    """Get or create recommendation service singleton."""
    global _rec_service
    if _rec_service is None:
        _rec_service = RecommendationService()
    return _rec_service
