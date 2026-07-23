"""Deterministic Plan Consistency Validator."""
from typing import Dict, Any, List


def validate_plan_consistency(response_plan: Dict[str, Any], priority_zones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate consistency between risk assessments and generated response directives."""
    violations = []
    if not response_plan:
        return violations

    items = response_plan.get("priority_action_items", [])
    
    # Check if high threat zones are omitted from plan
    planned_zones = {item.get("zone") for item in items}
    
    for zone in priority_zones:
        category = zone.get("category", "GREEN")
        zname = zone.get("zone_name", "Zone")
        
        if category in ["RED", "BLACK"]:
            if zname not in planned_zones:
                violations.append({
                    "code": "RISK_PLAN_MISMATCH",
                    "severity": "HIGH",
                    "message": f"High risk zone '{zname}' (Category: {category}) is missing from priority action items in response plan.",
                    "responsible_agent": "response_planner_agent",
                    "field": "response_plan.priority_action_items"
                })

            # Check for zero allocation when population is high
            for item in items:
                if item.get("zone") == zname:
                    res_alloc = item.get("allocated_resources", {})
                    if not res_alloc or sum(res_alloc.values()) == 0:
                        violations.append({
                            "code": "UNMET_CRITICAL_RESOURCE_NEED",
                            "severity": "CRITICAL",
                            "message": f"Critical risk zone '{zname}' requires emergency teams but zero resources are available in inventory.",
                            "responsible_agent": "resource_agent",
                            "field": "response_plan.priority_action_items.allocated_resources"
                        })

    return violations
