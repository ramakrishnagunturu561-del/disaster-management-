"""Deterministic Weather Telemetry & Data Age Validator."""
from datetime import datetime, timedelta
from typing import Dict, Any, List


def validate_weather(weather_intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate weather data age and source transparency."""
    violations = []
    if not weather_intelligence:
        violations.append({
            "code": "MISSING_WEATHER_DATA",
            "severity": "HIGH",
            "message": "No weather intelligence payload attached to current crisis state.",
            "responsible_agent": "weather_agent",
            "field": "weather_intelligence"
        })
        return violations

    status = weather_intelligence.get("status")
    timestamp_str = weather_intelligence.get("timestamp")

    if status == "UNAVAILABLE":
        violations.append({
            "code": "WEATHER_UNAVAILABLE_WARNING",
            "severity": "WARNING",
            "message": "Live weather API unavailable; using baseline metrics.",
            "responsible_agent": "weather_agent",
            "field": "weather_intelligence.status"
        })

    if timestamp_str:
        try:
            ts = datetime.fromisoformat(timestamp_str)
            age_minutes = (datetime.utcnow() - ts).total_seconds() / 60
            if age_minutes > 180:  # Older than 3 hours
                violations.append({
                    "code": "STALE_WEATHER",
                    "severity": "HIGH",
                    "message": f"Weather data is stale ({int(age_minutes)} minutes old).",
                    "responsible_agent": "weather_agent",
                    "field": "weather_intelligence.timestamp"
                })
        except Exception:
            pass

    return violations
