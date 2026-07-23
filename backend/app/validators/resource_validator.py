"""Deterministic Resource Allocation Validator."""
from typing import Dict, Any, List


def validate_resources(resource_plan: Dict[str, Any], initial_inventory: Dict[str, int]) -> List[Dict[str, Any]]:
    """Validate resource allocation against inventory limits.
    
    Checks:
    - allocated resources <= available resources
    - no negative quantities
    - no duplicate or nonexistent resource types
    """
    violations = []
    if not resource_plan:
        return violations

    allocated_totals = resource_plan.get("total_allocated", {})
    
    for rtype, allocated_count in allocated_totals.items():
        # Check negative quantity
        if allocated_count < 0:
            violations.append({
                "code": "NEGATIVE_RESOURCE_QUANTITY",
                "severity": "CRITICAL",
                "message": f"Resource type '{rtype}' allocated negative quantity {allocated_count}.",
                "responsible_agent": "resource_agent",
                "field": f"total_allocated.{rtype}"
            })
        
        # Check nonexistent resource
        if rtype not in initial_inventory:
            violations.append({
                "code": "NONEXISTENT_RESOURCE_TYPE",
                "severity": "CRITICAL",
                "message": f"Resource type '{rtype}' does not exist in available inventory.",
                "responsible_agent": "resource_agent",
                "field": f"total_allocated.{rtype}"
            })
            continue

        available = initial_inventory.get(rtype, 0)
        # Check over-allocation
        if allocated_count > available:
            violations.append({
                "code": "RESOURCE_OVERALLOCATED",
                "severity": "CRITICAL",
                "message": f"Resource '{rtype}' over-allocated: {allocated_count} planned > {available} available.",
                "responsible_agent": "resource_agent",
                "field": f"total_allocated.{rtype}",
                "evidence": {"planned": allocated_count, "available": available}
            })

    return violations
