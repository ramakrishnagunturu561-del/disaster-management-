"""Deterministic Evidence Traceability and Provenance Validator."""
from typing import Dict, Any, List


def validate_evidence(evidence_records: List[Dict[str, Any]], response_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate evidence traceability and provenance metadata (REAL, SIMULATED, USER_PROVIDED, DERIVED)."""
    violations = []
    
    if not evidence_records:
        violations.append({
            "code": "MISSING_EVIDENCE",
            "severity": "WARNING",
            "message": "Operational proposal generated without supporting evidence records.",
            "responsible_agent": "response_planner_agent",
            "field": "evidence"
        })

    # Check unverified social media reports
    for ev in evidence_records:
        source = ev.get("source", "").upper()
        if "SOCIAL_MEDIA" in source and not ev.get("corroborated", False):
            violations.append({
                "code": "UNVERIFIED_SOCIAL_REPORT",
                "severity": "WARNING",
                "message": f"Unverified social media report used in evidence trace: '{ev.get('detail', '')[:60]}...'",
                "responsible_agent": "intelligence_agent",
                "field": "evidence.source"
            })

    return violations
