"""Deterministic Shelter Capacity & Overflow Validator."""
from typing import Dict, Any, List


def validate_shelters(evacuation_plan: Dict[str, Any], priority_zones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate shelter capacity constraints across priority zones."""
    violations = []
    if not evacuation_plan:
        return violations

    shelter_occupancy: Dict[str, int] = {}

    for zone in priority_zones:
        zid = zone.get("zone_id") or zone.get("id")
        zname = zone.get("zone_name") or zone.get("name", "Zone")
        population = zone.get("population", 0)

        plan = evacuation_plan.get(zid, {})
        target_shelter = plan.get("target_shelter", "")
        remaining_cap = plan.get("shelter_capacity_remaining", 0)

        if not target_shelter:
            violations.append({
                "code": "MISSING_SHELTER_DESTINATION",
                "severity": "CRITICAL",
                "message": f"Zone '{zname}' requires evacuation but no target shelter destination assigned.",
                "responsible_agent": "route_agent",
                "field": f"evacuation_plan.{zid}.target_shelter"
            })
            continue

        if "UNAVAILABLE" in target_shelter.upper():
            violations.append({
                "code": "SHELTER_UNAVAILABLE",
                "severity": "CRITICAL",
                "message": f"Zone '{zname}' assigned to unavailable shelter: '{target_shelter}'.",
                "responsible_agent": "route_agent",
                "field": f"evacuation_plan.{zid}.target_shelter"
            })

        if remaining_cap < population or remaining_cap < 0:
            violations.append({
                "code": "SHELTER_CAPACITY_EXCEEDED",
                "severity": "CRITICAL",
                "message": f"Shelter capacity exceeded for zone '{zname}' (Evacuees {population:,} > remaining capacity {remaining_cap:,}).",
                "responsible_agent": "route_agent",
                "field": f"evacuation_plan.{zid}.shelter_capacity_remaining",
                "evidence": {"population": population, "capacity_remaining": remaining_cap}
            })

    return violations
