"""Deterministic Route Conflict and Hazard Validator."""
from typing import Dict, Any, List


def validate_routes(route_analysis: Dict[str, Any], evacuation_plan: Dict[str, Any], response_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate route safety against detected road blockages and bridge structural damage."""
    violations = []
    if not route_analysis:
        return violations

    blocked_corridors = route_analysis.get("blocked_corridors", [])

    # Check if plan references blocked corridor
    if response_plan:
        items = response_plan.get("priority_action_items", [])
        for item in items:
            used_route = item.get("route", "")
            zname = item.get("zone", "Zone")
            
            for blocked in blocked_corridors:
                if blocked.lower() in used_route.lower() or used_route.lower() in blocked.lower():
                    violations.append({
                        "code": "ROUTE_BLOCKED",
                        "severity": "CRITICAL",
                        "message": f"Evacuation plan for '{zname}' uses known blocked corridor: '{used_route}' (Conflict: {blocked}).",
                        "responsible_agent": "route_agent",
                        "field": "response_plan.priority_action_items",
                        "evidence": {"used_route": used_route, "blocked_hazard": blocked}
                    })

    if not blocked_corridors:
        violations.append({
            "code": "INCOMPLETE_HAZARD_COVERAGE",
            "severity": "WARNING",
            "message": "Hazard coverage check completed with zero detected road blockages; verify satellite/drone feed.",
            "responsible_agent": "route_agent",
            "field": "route_analysis.blocked_corridors"
        })

    return violations
