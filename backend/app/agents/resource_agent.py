"""Resource Allocation Agent with strict constraint validation."""
import logging
from typing import Dict, Any, List
from app.graph.crisis_state import CrisisState

logger = logging.getLogger(__name__)


class ResourceAllocationAgent:
    """Agent responsible for optimizing resource assignment (ambulances, boats, rescue teams, drones) 
    with zero constraint violations."""

    def __init__(self):
        self.name = "RESOURCE_AGENT"

    async def run(self, state: CrisisState) -> CrisisState:
        """Allocate available emergency resources across priority zones without over-allocation."""
        state.record_step(
            agent=self.name,
            action="ALLOCATE_RESOURCES",
            status="STARTED",
            summary="Evaluating resource availability and zone demand."
        )

        # Baseline inventory if none in state
        inventory = state.available_resources if bool(state.available_resources) else {
            "rescue_teams": 6,
            "rescue_boats": 4,
            "ambulances": 12,
            "drones": 4,
            "fire_trucks": 8
        }
        state.available_resources = inventory.copy()

        remaining = inventory.copy()
        allocations = {}
        allocated_totals = {k: 0 for k in inventory}

        for zone in state.priority_zones:
            zid = zone.get("zone_id", "zone_x")
            threat = zone.get("category", "GREEN")
            zname = zone.get("zone_name", zid)

            zone_alloc = {}

            if threat in ["BLACK", "RED"]:
                # High demand
                for rtype, available_count in remaining.items():
                    target = 3 if rtype in ["rescue_teams", "rescue_boats", "ambulances"] else 1
                    assigned = min(target, available_count)
                    if assigned > 0:
                        zone_alloc[rtype] = assigned
                        remaining[rtype] -= assigned
                        allocated_totals[rtype] += assigned

            elif threat == "YELLOW":
                for rtype, available_count in remaining.items():
                    target = 1
                    assigned = min(target, available_count)
                    if assigned > 0:
                        zone_alloc[rtype] = assigned
                        remaining[rtype] -= assigned
                        allocated_totals[rtype] += assigned

            allocations[zid] = {
                "zone_name": zname,
                "threat": threat,
                "assigned_resources": zone_alloc
            }

        # STRICT CONSTRAINT VALIDATION
        over_allocated = []
        for rtype, total_allocated in allocated_totals.items():
            if total_allocated > inventory.get(rtype, 0):
                over_allocated.append(f"{rtype}: allocated {total_allocated} > available {inventory.get(rtype, 0)}")

        if over_allocated:
            state.warnings.append(f"Resource constraint violation detected: {', '.join(over_allocated)}")
            state.record_step(
                agent=self.name,
                action="ALLOCATE_RESOURCES",
                status="FAILED",
                summary="Resource constraint check failed due to over-allocation.",
                confidence=0.0,
                errors=over_allocated
            )
            return state

        state.resource_plan = {
            "initial_inventory": inventory,
            "allocations": allocations,
            "remaining_inventory": remaining,
            "total_allocated": allocated_totals,
            "status": "VALIDATED"
        }

        summary_msg = (
            f"Resource allocation completed with zero constraint violations. "
            f"Allocated: {allocated_totals.get('rescue_teams', 0)} rescue teams, {allocated_totals.get('ambulances', 0)} ambulances, "
            f"{allocated_totals.get('rescue_boats', 0)} boats across {len(allocations)} zones."
        )

        state.record_step(
            agent=self.name,
            action="ALLOCATE_RESOURCES",
            status="COMPLETED",
            summary=summary_msg,
            confidence=0.98
        )

        return state
